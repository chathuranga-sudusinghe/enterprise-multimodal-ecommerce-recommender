"""Validate local processed artifacts for Data Gate hardening.

This script is intentionally lightweight and local. It records validation
evidence for processed artifacts; it is not production monitoring.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_PATH = PROJECT_ROOT / "docs/reports/data_quality_validation_report.md"

ABO_CLEAN_JSONL_FILES = (
    "abo_clean_products_5k.jsonl",
    "abo_clean_products_sample.jsonl",
)
SIMILARITY_JSON_FILES = (
    "abo_tfidf_similarity_5k_sample.json",
    "abo_image_similarity_5k_sample.json",
    "abo_clip_similarity_5k_sample.json",
)
EVALUATION_JSON_FILES = (
    "abo_similarity_proxy_evaluation.json",
    "retailrocket_baseline_evaluation.json",
)
QUERY_FIELDS = (
    "query_item_id",
    "source_product_id",
    "query_product_id",
    "query_image_id",
    "source_image_id",
)
COMMON_METRIC_HINTS = (
    "hit_rate",
    "recall",
    "precision",
    "ndcg",
    "map",
    "mrr",
    "coverage",
)


@dataclass
class ValidationResult:
    """Validation evidence for one expected processed artifact."""

    path: Path
    artifact_type: str
    status: str
    summary: str
    counters: dict[str, int] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    top_level_keys: list[str] = field(default_factory=list)

    @property
    def exists(self) -> bool:
        return self.status != "MISSING"


def validate_processed_data(
    processed_dir: Path = PROJECT_ROOT / "data/processed",
) -> list[ValidationResult]:
    """Validate known local processed artifacts if they exist."""
    results: list[ValidationResult] = []
    for filename in ABO_CLEAN_JSONL_FILES:
        results.append(validate_abo_clean_jsonl(processed_dir / filename))
    for filename in SIMILARITY_JSON_FILES:
        results.append(validate_similarity_json(processed_dir / filename))
    for filename in EVALUATION_JSON_FILES:
        results.append(validate_evaluation_json(processed_dir / filename))
    return results


def validate_abo_clean_jsonl(path: Path) -> ValidationResult:
    """Validate cleaned ABO product JSONL without modifying the artifact."""
    if not path.is_file():
        return _missing(path, "ABO cleaned JSONL")

    counters = {
        "records": 0,
        "invalid_json_lines": 0,
        "non_object_records": 0,
        "missing_item_id": 0,
        "duplicate_item_id": 0,
        "missing_product_type": 0,
        "missing_image_path": 0,
        "is_clip_ready_true": 0,
        "is_clip_ready_false": 0,
        "is_clip_ready_non_boolean": 0,
    }
    issues: list[str] = []
    seen_item_ids: set[str] = set()
    saw_clip_ready = False

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            counters["records"] += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                counters["invalid_json_lines"] += 1
                issues.append(f"Line {line_number} is invalid JSON: {exc.msg}")
                continue
            if not isinstance(record, Mapping):
                counters["non_object_records"] += 1
                issues.append(f"Line {line_number} is not a JSON object.")
                continue

            item_id = _string_value(record.get("item_id"))
            if not item_id:
                counters["missing_item_id"] += 1
            elif item_id in seen_item_ids:
                counters["duplicate_item_id"] += 1
            else:
                seen_item_ids.add(item_id)

            if not _has_value(record.get("product_type")):
                counters["missing_product_type"] += 1
            if not _has_value(record.get("image_path")):
                counters["missing_image_path"] += 1

            if "is_clip_ready" in record:
                saw_clip_ready = True
                if record["is_clip_ready"] is True:
                    counters["is_clip_ready_true"] += 1
                elif record["is_clip_ready"] is False:
                    counters["is_clip_ready_false"] += 1
                else:
                    counters["is_clip_ready_non_boolean"] += 1

    if not saw_clip_ready:
        counters.pop("is_clip_ready_true")
        counters.pop("is_clip_ready_false")
        counters.pop("is_clip_ready_non_boolean")

    if counters["records"] == 0:
        issues.append("JSONL file contains no product records.")
    status = _status_from_issue_counts(
        fail_count=counters["invalid_json_lines"] + counters["non_object_records"],
        warn_count=(
            counters["missing_item_id"]
            + counters["duplicate_item_id"]
            + counters["missing_product_type"]
            + counters["missing_image_path"]
            + counters.get("is_clip_ready_non_boolean", 0)
            + (1 if counters["records"] == 0 else 0)
        ),
    )
    return ValidationResult(
        path=path,
        artifact_type="ABO cleaned JSONL",
        status=status,
        summary=f"Validated {counters['records']} cleaned ABO product records.",
        counters=counters,
        issues=issues,
    )


def validate_similarity_json(path: Path) -> ValidationResult:
    """Validate a local ABO similarity output JSON artifact."""
    if not path.is_file():
        return _missing(path, "ABO similarity JSON")

    payload, parse_error = _load_json(path)
    if parse_error:
        return ValidationResult(
            path=path,
            artifact_type="ABO similarity JSON",
            status="FAIL",
            summary="File is not valid JSON.",
            issues=[parse_error],
        )
    if not isinstance(payload, Mapping):
        return ValidationResult(
            path=path,
            artifact_type="ABO similarity JSON",
            status="FAIL",
            summary="Similarity output must be a JSON object.",
            issues=["Top-level JSON value is not an object."],
        )

    top_level_keys = sorted(str(key) for key in payload)
    query_field, query_value = _first_present_query(payload)
    recommendations = payload.get("recommendations")
    counters = {
        "recommendations": 0,
        "missing_recommendation_item_id": 0,
        "duplicate_recommendations": 0,
        "self_recommendations": 0,
        "non_object_recommendations": 0,
    }
    issues: list[str] = []

    if query_field:
        issues.append(f"Query field present: {query_field}.")
    else:
        issues.append("No recognized query field is present.")

    if not isinstance(recommendations, list):
        return ValidationResult(
            path=path,
            artifact_type="ABO similarity JSON",
            status="FAIL",
            summary="Recommendations list is missing or malformed.",
            counters=counters,
            issues=issues + ["Expected top-level `recommendations` list."],
            top_level_keys=top_level_keys,
        )

    seen_recommendations: set[str] = set()
    query_item_id = _string_value(query_value) if query_field and "item" in query_field else ""
    for index, recommendation in enumerate(recommendations, start=1):
        counters["recommendations"] += 1
        if not isinstance(recommendation, Mapping):
            counters["non_object_recommendations"] += 1
            issues.append(f"Recommendation {index} is not a JSON object.")
            continue

        item_id = _string_value(recommendation.get("item_id"))
        image_id = _string_value(recommendation.get("image_id"))
        recommendation_key = item_id or image_id or json.dumps(recommendation, sort_keys=True)
        if not item_id and not image_id:
            counters["missing_recommendation_item_id"] += 1
        if recommendation_key in seen_recommendations:
            counters["duplicate_recommendations"] += 1
        else:
            seen_recommendations.add(recommendation_key)
        if query_item_id and item_id == query_item_id:
            counters["self_recommendations"] += 1

    status = _status_from_issue_counts(
        fail_count=counters["non_object_recommendations"],
        warn_count=(
            counters["missing_recommendation_item_id"]
            + counters["duplicate_recommendations"]
            + counters["self_recommendations"]
            + (1 if not query_field else 0)
        ),
    )
    return ValidationResult(
        path=path,
        artifact_type="ABO similarity JSON",
        status=status,
        summary=f"Validated {counters['recommendations']} similarity recommendations.",
        counters=counters,
        issues=issues,
        top_level_keys=top_level_keys,
    )


def validate_evaluation_json(path: Path) -> ValidationResult:
    """Validate a local evaluation JSON artifact."""
    if not path.is_file():
        return _missing(path, "Evaluation JSON")

    payload, parse_error = _load_json(path)
    if parse_error:
        return ValidationResult(
            path=path,
            artifact_type="Evaluation JSON",
            status="FAIL",
            summary="File is not valid JSON.",
            issues=[parse_error],
        )
    if not isinstance(payload, Mapping):
        return ValidationResult(
            path=path,
            artifact_type="Evaluation JSON",
            status="FAIL",
            summary="Evaluation output must be a JSON object.",
            issues=["Top-level JSON value is not an object."],
        )

    top_level_keys = sorted(str(key) for key in payload)
    metric_keys = _metric_like_keys(payload)
    issues = [f"Top-level keys available: {', '.join(top_level_keys) or '(none)'}."] 
    if metric_keys:
        issues.append(f"Metric-like fields present: {', '.join(metric_keys)}.")
    elif "metrics_by_method" in payload:
        issues.append("Nested `metrics_by_method` field is present.")
    else:
        issues.append("No common metric fields detected at the top level.")

    return ValidationResult(
        path=path,
        artifact_type="Evaluation JSON",
        status="PASS" if metric_keys or "metrics_by_method" in payload else "WARN",
        summary="Evaluation JSON parsed successfully.",
        counters={"top_level_key_count": len(top_level_keys), "metric_like_key_count": len(metric_keys)},
        issues=issues,
        top_level_keys=top_level_keys,
    )


def render_report(
    results: Sequence[ValidationResult],
    processed_dir: Path = PROJECT_ROOT / "data/processed",
    generated_at_utc: str | None = None,
) -> str:
    """Render a markdown validation report for docs/reports."""
    generated_at_utc = generated_at_utc or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    summary_counts = _count_statuses(results)
    missing = [result for result in results if result.status == "MISSING"]
    failures = [result for result in results if result.status == "FAIL"]
    warnings = [result for result in results if result.status == "WARN"]

    lines = [
        "# Data Quality Validation Report",
        "",
        "## Purpose",
        "",
        "This report records the first lightweight local validation evidence for the Data Gate Hardening milestone. It validates processed artifacts if they exist and does not modify raw data or processed artifacts.",
        "",
        "This is local validation evidence, not production monitoring.",
        "",
        "## Run Context",
        "",
        f"- Generated at UTC: `{generated_at_utc}`",
        f"- Processed directory: `{_display_path(processed_dir)}`",
        "- Validator: `scripts/validate_processed_data.py`",
        "",
        "## Pass/Warn/Fail Summary",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status in ("PASS", "WARN", "FAIL", "MISSING"):
        lines.append(f"| {status} | {summary_counts.get(status, 0)} |")

    lines.extend(
        [
            "",
            "## Files Checked",
            "",
            "| File | Type | Status | Summary |",
            "|---|---|---|---|",
        ]
    )
    for result in results:
        lines.append(
            f"| `{_display_path(result.path)}` | {result.artifact_type} | {result.status} | {result.summary} |"
        )

    lines.extend(["", "## Missing Files", ""])
    if missing:
        lines.extend(f"- `{_display_path(result.path)}`" for result in missing)
    else:
        lines.append("- None.")

    lines.extend(["", "## Schema Issues", ""])
    _append_issue_section(lines, results, include_statuses={"FAIL", "WARN", "PASS"})

    lines.extend(["", "## Duplicate Issues", ""])
    duplicate_lines = _counter_lines(results, ("duplicate_item_id", "duplicate_recommendations"))
    lines.extend(duplicate_lines or ["- None detected."])

    lines.extend(["", "## Missing Value Counts", ""])
    missing_value_lines = _counter_lines(
        results,
        (
            "missing_item_id",
            "missing_product_type",
            "missing_image_path",
            "missing_recommendation_item_id",
        ),
    )
    lines.extend(missing_value_lines or ["- None detected."])

    lines.extend(["", "## Data Gate Impact", ""])
    if failures:
        lines.append("- Data Gate impact: FAIL issues are present in local processed artifacts. These must be resolved or explicitly accepted before Data Gate can be marked GO.")
    elif warnings:
        lines.append("- Data Gate impact: no malformed processed artifacts were detected, but warnings remain. Data Gate should stay Partial until warnings are reviewed and validation coverage is approved.")
    else:
        lines.append("- Data Gate impact: all existing checked processed artifacts passed this lightweight validation. Missing optional local artifacts, if any, still need review before broader Data Gate approval.")
    lines.extend(
        [
            "- This report supports documentation and data contract hardening only.",
            "- This report does not authorize FAISS, vector DB, API, MCP, deployment, monitoring, or production-readiness claims.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(report: str, output_path: Path = DEFAULT_REPORT_PATH) -> None:
    """Write the markdown validation report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=PROJECT_ROOT / "data/processed")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    results = validate_processed_data(args.processed_dir)
    write_report(render_report(results, args.processed_dir), args.report)
    print(f"Wrote data quality validation report: {_display_path(args.report)}")
    return 1 if any(result.status == "FAIL" for result in results) else 0


def _missing(path: Path, artifact_type: str) -> ValidationResult:
    return ValidationResult(
        path=path,
        artifact_type=artifact_type,
        status="MISSING",
        summary="File is missing; recorded as missing evidence, not a validation failure.",
    )


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}."


def _first_present_query(payload: Mapping[str, Any]) -> tuple[str | None, Any | None]:
    for field_name in QUERY_FIELDS:
        if field_name in payload:
            return field_name, payload[field_name]
    query_product = payload.get("query_product")
    if isinstance(query_product, Mapping) and "item_id" in query_product:
        return "query_product.item_id", query_product["item_id"]
    return None, None


def _metric_like_keys(payload: Mapping[str, Any]) -> list[str]:
    keys: list[str] = []
    for key in payload:
        key_text = str(key).lower()
        if any(hint in key_text for hint in COMMON_METRIC_HINTS):
            keys.append(str(key))
    return sorted(keys)


def _status_from_issue_counts(fail_count: int, warn_count: int) -> str:
    if fail_count:
        return "FAIL"
    if warn_count:
        return "WARN"
    return "PASS"


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return len(value) > 0
    return True


def _string_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _count_statuses(results: Iterable[ValidationResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    return counts


def _append_issue_section(
    lines: list[str],
    results: Sequence[ValidationResult],
    include_statuses: set[str],
) -> None:
    found = False
    for result in results:
        if result.status not in include_statuses or not result.issues:
            continue
        found = True
        lines.append(f"- `{_display_path(result.path)}` ({result.status}):")
        for issue in result.issues:
            lines.append(f"  - {issue}")
    if not found:
        lines.append("- None detected.")


def _counter_lines(results: Sequence[ValidationResult], counter_names: Sequence[str]) -> list[str]:
    lines: list[str] = []
    for result in results:
        relevant = {
            name: count
            for name, count in result.counters.items()
            if name in counter_names and count
        }
        if not relevant:
            continue
        counters = ", ".join(f"{name}={count}" for name, count in relevant.items())
        lines.append(f"- `{_display_path(result.path)}`: {counters}")
    return lines


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
