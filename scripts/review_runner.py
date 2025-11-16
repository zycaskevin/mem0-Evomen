from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from review_tools import (
    cross_validate,
    ensure_directory,
    load_config,
    project_root,
    read_json,
    to_absolute,
    utc_timestamp,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Codex and/or Gemini reviews using workspace defaults.",
    )
    parser.add_argument(
        "--type",
        choices=["plan", "code"],
        default="code",
        help="Review type. Defaults to code.",
    )
    parser.add_argument(
        "--input",
        help="Path to review target. Overrides config defaults when provided.",
    )
    parser.add_argument(
        "--output",
        help="Directory for review artifacts. Defaults to config -> output_dir.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        help="Subset of models to run (codex, gemini). Defaults to all enabled.",
    )
    parser.add_argument(
        "--config",
        help="Custom review_config.yaml path.",
    )
    parser.add_argument(
        "--timestamp",
        help="Force timestamp suffix (useful for reproduction).",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip cross validation step even when both models run.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved commands without executing them.",
    )
    return parser.parse_args()


class ReviewError(RuntimeError):
    pass


def resolve_input_path(review_type: str, cfg: Dict[str, Any], value: str | None) -> Path:
    defaults = cfg.get("defaults", {})
    if value:
        return to_absolute(value)
    if review_type == "plan":
        return to_absolute(defaults.get("plan_input", "docs/plan.md"))
    return to_absolute(defaults.get("code_input", "src"))


def resolve_output_dir(cfg: Dict[str, Any], value: str | None) -> Path:
    defaults = cfg.get("defaults", {})
    output_dir = value or defaults.get("output_dir", "data/reviews")
    return ensure_directory(to_absolute(output_dir))


def enabled_models(cfg: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    models = cfg.get("models", {})
    if not models:
        raise ReviewError("review_config.yaml 未定義任何模型。")
    enabled = {
        name.lower(): details
        for name, details in models.items()
        if details.get("enabled", True)
    }
    if not enabled:
        raise ReviewError("review_config.yaml 沒有啟用的模型。")
    return enabled


def build_command(args_template: List[str], context: Dict[str, str]) -> List[str]:
    command = []
    for item in args_template:
        formatted = item.format(**context)
        if formatted:
            command.append(formatted)
    return command


def run_single_model(
    model_name: str,
    model_cfg: Dict[str, Any],
    context: Dict[str, str],
    cwd: Path,
    dry_run: bool = False,
) -> Path:
    args_template = model_cfg.get("args")
    if not args_template:
        raise ReviewError(f"{model_name} 模型缺少 args 設定。")

    output_name = model_cfg.get(
        "output_name",
        f"{model_name}_{context['type']}_{context['timestamp']}.json",
    )
    output_path = ensure_directory(Path(context["output_dir"])) / output_name
    format_tokens = context | {"output_file": str(output_path)}
    command = build_command(args_template, format_tokens)
    env = os.environ.copy()
    for key, value in (model_cfg.get("env") or {}).items():
        env[key] = value.format(**format_tokens)

    if dry_run:
        print(f"[DRY-RUN] {' '.join(command)}")
        return output_path

    print(f"[review] Running {model_name} -> {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
    except FileNotFoundError as exc:
        raise ReviewError(f"找不到指令：{command[0]}") from exc

    if result.returncode != 0:
        raise ReviewError(
            f"{model_name} 審查失敗 (exit {result.returncode}):\n{result.stderr}"
        )

    capture_stdout = model_cfg.get("capture_stdout", True)
    validate_json = model_cfg.get("validate_json", True)

    if capture_stdout:
        payload = result.stdout.strip()
        if not payload:
            raise ReviewError(f"{model_name} 沒有輸出任何內容。")
        if validate_json:
            try:
                json.loads(payload)
            except json.JSONDecodeError as err:
                raise ReviewError(
                    f"{model_name} STDOUT 無法解析為 JSON: {err}"
                ) from err
        output_path.write_text(payload, encoding="utf-8")
    else:
        expected = model_cfg.get("expected_output", "{output_file}").format(**format_tokens)
        expected_path = Path(expected)
        if not expected_path.is_absolute():
            expected_path = output_path.parent / expected_path
        if not expected_path.exists():
            raise ReviewError(
                f"{model_name} 未建立預期的輸出檔 ({expected_path})."
            )
        output_path.write_text(expected_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"[review] {model_name} 輸出 -> {output_path}")
    return output_path


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    models = enabled_models(cfg)

    requested = [m.lower() for m in (args.models or list(models.keys()))]
    invalid = [m for m in requested if m not in models]
    if invalid:
        raise ReviewError(f"未知模型: {', '.join(invalid)}")

    review_type = args.type
    input_path = resolve_input_path(review_type, cfg, args.input)
    if not input_path.exists():
        raise ReviewError(f"找不到指定的輸入路徑: {input_path}")

    output_dir = resolve_output_dir(cfg, args.output)
    timestamp = args.timestamp or utc_timestamp(cfg.get("defaults", {}).get("timestamp_format", "%Y%m%dT%H%M%SZ"))
    root = project_root()

    context = {
        "type": review_type,
        "input": str(input_path),
        "output_dir": str(output_dir),
        "timestamp": timestamp,
        "project_root": str(root),
    }

    produced: Dict[str, Path] = {}
    for model_name in requested:
        output_path = run_single_model(
            model_name,
            models[model_name],
            context,
            cwd=root,
            dry_run=args.dry_run,
        )
        produced[model_name] = output_path

    if args.dry_run:
        print("[DRY-RUN] 未執行實際審查。")
        return

    if (
        not args.skip_validation
        and "codex" in produced
        and "gemini" in produced
        and cfg.get("validation", {}).get("enabled", True)
    ):
        codex_payload = read_json(produced["codex"])
        gemini_payload = read_json(produced["gemini"])
        validation = cross_validate(codex_payload, gemini_payload, cfg.get("validation"))
        validation_path = output_dir / f"validation_{review_type}_{timestamp}.json"
        write_json(validation_path, validation)
        print(f"[review] Cross validation -> {validation_path} ({validation['status']})")
    else:
        print("[review] Cross validation skipped.")


if __name__ == "__main__":
    try:
        main()
    except ReviewError as exc:
        print(f"[review:error] {exc}", file=sys.stderr)
        sys.exit(1)
