"""Run live-browser QA for the exact BurnLens offline reviewer handoff."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zipfile

from .label_review_browser_qa import (
    LabelReviewBrowserQaError,
    run_browser_qa,
    write_browser_qa_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--browser-executable", type=Path, required=True)
    parser.add_argument("--node-executable", type=Path, required=True)
    parser.add_argument("--work-directory", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    parser.add_argument("--output-desktop-png", type=Path, required=True)
    parser.add_argument("--output-mobile-png", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--git-source-commit", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report, raw_paths = run_browser_qa(
            archive_path=args.archive,
            packet_path=args.packet,
            browser_executable=args.browser_executable,
            node_executable=args.node_executable,
            work_directory=args.work_directory,
            run_id=args.run_id,
            git_source_commit=args.git_source_commit,
        )
        write_browser_qa_outputs(
            report,
            raw_paths,
            json_path=args.output_json,
            html_path=args.output_html,
            png_path=args.output_png,
            desktop_path=args.output_desktop_png,
            mobile_path=args.output_mobile_png,
        )
        print(report["decision"])
        print(f"browser={report['browser_runtime']['product']}")
        print(f"response_fixture_sha256={report['checks']['response_fixture']['sha256']}")
        return 0
    except (
        LabelReviewBrowserQaError,
        OSError,
        ValueError,
        KeyError,
        zipfile.BadZipFile,
    ) as error:
        print(f"LABEL_REVIEW_BROWSER_QA_FAILED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
