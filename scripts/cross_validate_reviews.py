from __future__ import annotations

import argparse
import sys
from pathlib import Path

from review_tools import (
    cross_validate,
    load_config,
    read_json,
    to_absolute,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cross validate Codex/Gemini review JSON artifacts.",
    )
    parser.add_argument("--codex", required=True, help="Path to codex review JSON.")
    parser.add_argument("--gemini", required=True, help="Path to gemini review JSON.")
    parser.add_argument(
        "--output",
        help="Output path for validation result. Defaults to same directory.",
    )
    parser.add_argument(
        "--config",
        help="Custom review_config.yaml path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    codex_path = to_absolute(args.codex)
    gemini_path = to_absolute(args.gemini)

    if not codex_path.exists():
        raise FileNotFoundError(f"找不到 codex 檔案: {codex_path}")
    if not gemini_path.exists():
        raise FileNotFoundError(f"找不到 gemini 檔案: {gemini_path}")

    codex_payload = read_json(codex_path)
    gemini_payload = read_json(gemini_path)
    validation = cross_validate(codex_payload, gemini_payload, cfg.get("validation"))

    if args.output:
        output_path = to_absolute(args.output)
    else:
        output_path = codex_path.parent / f"validation_manual_{validation['timestamp']}.json"
    write_json(output_path, validation)
    print(f"Cross validation {validation['status']} -> {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[cross-validate:error] {exc}", file=sys.stderr)
        sys.exit(1)
