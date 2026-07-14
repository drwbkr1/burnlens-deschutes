"""Rebuild the human-readable access evidence from normalized JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .access_integrity import render_html, render_png


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-json", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    parser.add_argument("--output-png", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = json.loads(args.input_json.read_text(encoding="utf-8"))
    args.output_html.parent.mkdir(parents=True, exist_ok=True)
    args.output_html.write_text(render_html(report), encoding="utf-8")
    render_png(report, args.output_png)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
