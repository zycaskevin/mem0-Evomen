from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def project_root() -> Path:
    """Return the workspace root (two levels up from this file)."""
    return Path(__file__).resolve().parents[2]


def default_config_path() -> Path:
    """Return the default path of review_config.yaml."""
    return project_root() / ".claude" / "review_config.yaml"


def load_config(custom_path: Optional[str] = None) -> Dict[str, Any]:
    """Load YAML config and fall back to defaults when the file is missing."""
    path = Path(custom_path) if custom_path else default_config_path()
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    return {}


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def to_absolute(value: str, root: Optional[Path] = None) -> Path:
    root = root or project_root()
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def utc_timestamp(fmt: str = "%Y%m%dT%H%M%SZ") -> str:
    return _dt.datetime.utcnow().strftime(fmt)


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def lower_key(issue: Dict[str, Any]) -> str:
    description = issue.get("description") or ""
    location = issue.get("location") or ""
    return f"{description.strip().lower()}::{location.strip().lower()}"


def cross_validate(
    codex_review: Dict[str, Any],
    gemini_review: Dict[str, Any],
    cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    cfg = cfg or {}
    threshold = float(cfg.get("score_diff_threshold", 2.0))
    pass_threshold = float(cfg.get("pass_threshold", 8.0))
    require_both = bool(cfg.get("require_both", True))
    high_blocks = bool(cfg.get("high_severity_blocks", True))

    codex_score = float(codex_review.get("overall_score", 0.0))
    gemini_score = float(gemini_review.get("overall_score", 0.0))
    score_diff = abs(codex_score - gemini_score)

    codex_issues = codex_review.get("issues") or []
    gemini_issues = gemini_review.get("issues") or []
    high_severity = [
        issue
        for issue in (codex_issues + gemini_issues)
        if (issue.get("severity") or "").lower() == "high"
    ]

    codex_keys = {lower_key(item) for item in codex_issues}
    common_issues = [
        issue for issue in gemini_issues if lower_key(issue) in codex_keys
    ]

    status = "pass"
    action = "proceed"
    reasons = []

    if require_both and (
        codex_score < pass_threshold or gemini_score < pass_threshold
    ):
        status = "fail"
        action = "fix_required"
        reasons.append("One or both models scored below threshold")

    if score_diff > threshold:
        status = "disagreement"
        action = "human_review"
        reasons.append(f"Score difference {score_diff:.2f} > {threshold}")

    if high_blocks and high_severity:
        status = "fail"
        action = "fix_required"
        reasons.append("High severity issues detected")

    return {
        "status": status,
        "action": action,
        "codex_score": codex_score,
        "gemini_score": gemini_score,
        "score_diff": score_diff,
        "common_issue_count": len(common_issues),
        "high_severity_issues": high_severity,
        "common_issues": common_issues,
        "reasons": reasons,
        "timestamp": utc_timestamp(),
    }


__all__ = [
    "cross_validate",
    "default_config_path",
    "ensure_directory",
    "load_config",
    "project_root",
    "read_json",
    "to_absolute",
    "utc_timestamp",
    "write_json",
]
