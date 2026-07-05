"""Write raw dataset source, size, checksum, and Git ignore evidence."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "docs/reports/raw_dataset_source_and_checksum_report.md"
CHUNK_SIZE = 8 * 1024 * 1024


@dataclass(frozen=True)
class RawFileSpec:
    """Expected raw dataset file."""

    track: str
    purpose: str
    path: Path


EXPECTED_RAW_FILES = (
    RawFileSpec(
        "RetailRocket event-based recommendation",
        "Behavior/event recommendation raw events",
        PROJECT_ROOT / "data/raw/RetailRocket_event-based/events.csv",
    ),
    RawFileSpec(
        "RetailRocket event-based recommendation",
        "RetailRocket item properties part 1",
        PROJECT_ROOT / "data/raw/RetailRocket_event-based/item_properties_part1.csv",
    ),
    RawFileSpec(
        "RetailRocket event-based recommendation",
        "RetailRocket item properties part 2",
        PROJECT_ROOT / "data/raw/RetailRocket_event-based/item_properties_part2.csv",
    ),
    RawFileSpec(
        "RetailRocket event-based recommendation",
        "RetailRocket category hierarchy",
        PROJECT_ROOT / "data/raw/RetailRocket_event-based/category_tree.csv",
    ),
    RawFileSpec(
        "Amazon Berkeley Objects text/image similarity",
        "ABO listing metadata archive",
        PROJECT_ROOT / "data/raw/amazon_berkeley_text_images-based/abo-listings.tar",
    ),
    RawFileSpec(
        "Amazon Berkeley Objects text/image similarity",
        "ABO small image archive",
        PROJECT_ROOT / "data/raw/amazon_berkeley_text_images-based/abo-images-small.tar",
    ),
    RawFileSpec(
        "Amazon Berkeley Objects text/image similarity",
        "ABO local README/source notes",
        PROJECT_ROOT / "data/raw/amazon_berkeley_text_images-based/README.md",
    ),
)


def sha256_file(path: Path, chunk_size: int = CHUNK_SIZE) -> str:
    """Return a SHA256 digest while reading the file in bounded chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_raw_files(specs: Sequence[RawFileSpec] = EXPECTED_RAW_FILES) -> list[dict[str, object]]:
    """Inspect expected raw files without modifying or loading them into memory."""
    rows: list[dict[str, object]] = []
    for spec in specs:
        exists = spec.path.is_file()
        rows.append(
            {
                "track": spec.track,
                "purpose": spec.purpose,
                "path": _display_path(spec.path),
                "exists": exists,
                "size_bytes": spec.path.stat().st_size if exists else None,
                "sha256": sha256_file(spec.path) if exists else None,
                "git_ignored": _git_check_ignore(spec.path),
                "git_tracked": _git_is_tracked(spec.path),
            }
        )
    return rows


def render_report(rows: Sequence[dict[str, object]], generated_at_utc: str | None = None) -> str:
    """Render the raw dataset checksum evidence report."""
    generated_at_utc = generated_at_utc or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    retailrocket_rows = [row for row in rows if str(row["track"]).startswith("RetailRocket")]
    abo_rows = [row for row in rows if str(row["track"]).startswith("Amazon Berkeley Objects")]

    lines = [
        "# Raw Dataset Source and Checksum Report",
        "",
        "## Purpose",
        "",
        "This report records local raw dataset file presence, file sizes, SHA256 checksums, and Git ignore evidence for the Data Gate Hardening milestone.",
        "",
        "The report is evidence only. It does not modify raw data, commit raw data, implement FAISS, vector databases, APIs, MCP, deployment, monitoring, or production features.",
        "",
        "Raw files are not committed and must not be committed.",
        "",
        "## Run Context",
        "",
        f"- Generated at UTC: `{generated_at_utc}`",
        "- Reporter: `scripts/report_raw_dataset_sources.py`",
        "- Hashing method: SHA256 with bounded chunked file reads",
        "",
        "## Raw Dataset Tracks",
        "",
        "| Track | Purpose | Local folder |",
        "|---|---|---|",
        "| RetailRocket event-based recommendation | Behavior/event recommendation | `data/raw/RetailRocket_event-based/` |",
        "| Amazon Berkeley Objects text/image similarity | Product metadata, text, and image similarity | `data/raw/amazon_berkeley_text_images-based/` |",
        "",
        "## Expected Raw Files for RetailRocket",
        "",
        *_expected_file_lines(retailrocket_rows),
        "",
        "## Expected Raw Files for ABO",
        "",
        *_expected_file_lines(abo_rows),
        "",
        "## Local File Presence, Sizes, and Checksums",
        "",
        "| Track | Path | Present | Size bytes | Size MiB | SHA256 |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        size_bytes = row["size_bytes"]
        lines.append(
            "| {track} | `{path}` | {present} | {size_bytes} | {size_mib} | `{sha256}` |".format(
                track=row["track"],
                path=row["path"],
                present="yes" if row["exists"] else "no",
                size_bytes=size_bytes if size_bytes is not None else "",
                size_mib=_format_mib(size_bytes),
                sha256=row["sha256"] or "",
            )
        )

    lines.extend(
        [
            "",
            "## Raw Data Git Ignore Status",
            "",
            "Repository `.gitignore` includes `data/raw/*` and preserves `data/raw/.gitkeep`.",
            "",
            "| Path | Git ignored | Git tracked |",
            "|---|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['path']}` | {'yes' if row['git_ignored'] else 'no'} | {'yes' if row['git_tracked'] else 'no'} |"
        )

    any_missing = any(not row["exists"] for row in rows)
    any_tracked = any(row["git_tracked"] for row in rows)
    all_ignored = all(row["git_ignored"] for row in rows if row["exists"])
    lines.extend(
        [
            "",
            "## Source and Provenance Notes",
            "",
            "- RetailRocket raw files are local copies for the event-based recommendation track.",
            "- ABO raw files are local copies for the product metadata, text similarity, and image similarity track.",
            "- The two dataset tracks are independent and must not be joined or treated as one catalog, user system, or business source.",
            "- Upstream source URLs, exact download timestamps, and upstream-provided checksums are not fully captured in this report.",
            "- Local SHA256 checksums in this report identify the files currently present in this workspace.",
            "",
            "## Data Gate Impact",
            "",
        ]
    )
    if any_tracked:
        lines.append("- Data Gate impact: NO-GO. One or more expected raw files appear to be tracked by Git and must be removed from version control without deleting local raw data.")
    elif any_missing:
        lines.append("- Data Gate impact: PARTIAL. One or more expected raw files are missing locally, so raw dataset readiness is incomplete.")
    elif not all_ignored:
        lines.append("- Data Gate impact: PARTIAL. Expected raw files are present, but at least one file is not ignored by Git.")
    else:
        lines.append("- Data Gate impact: local raw file presence, checksum evidence, and Git ignore evidence are available for expected raw files.")
        lines.append("- This strengthens Data Gate evidence but does not by itself make the full Data Gate GO.")

    lines.extend(
        [
            "- Raw data must remain local under `data/raw/` and must not be committed.",
            "- This report supports documentation and evidence hardening only.",
            "",
            "## Limitations",
            "",
            "- Checksums are local workspace checksums, not upstream authenticity guarantees.",
            "- The report does not validate schemas, row counts, missing values, or model quality.",
            "- The report does not prove source licensing compliance by itself.",
            "- The report does not authorize FAISS, vector DB, API, MCP, deployment, monitoring, or production-readiness work.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(report: str, output_path: Path = DEFAULT_OUTPUT) -> None:
    """Write the markdown report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    rows = inspect_raw_files()
    write_report(render_report(rows), args.output)
    print(f"Wrote raw dataset source and checksum report: {_display_path(args.output)}")
    return 0


def _expected_file_lines(rows: Sequence[dict[str, object]]) -> list[str]:
    lines = ["| Path | Purpose |", "|---|---|"]
    lines.extend(f"| `{row['path']}` | {row['purpose']} |" for row in rows)
    return lines


def _format_mib(size_bytes: object) -> str:
    if not isinstance(size_bytes, int):
        return ""
    return f"{size_bytes / (1024 * 1024):.2f}"


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def _git_check_ignore(path: Path) -> bool:
    result = _run_git("check-ignore", "-q", "--", _display_path(path))
    return result.returncode == 0


def _git_is_tracked(path: Path) -> bool:
    result = _run_git("ls-files", "--error-unmatch", "--", _display_path(path))
    return result.returncode == 0


def _run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={PROJECT_ROOT.as_posix()}",
            "-C",
            str(PROJECT_ROOT),
            *args,
        ],
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
