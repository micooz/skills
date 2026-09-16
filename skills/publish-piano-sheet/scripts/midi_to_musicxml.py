#!/usr/bin/env python3
"""Convert MIDI to MusicXML with useful title and credit metadata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a MIDI file to MusicXML using music21."
    )
    parser.add_argument("input", type=Path, help="Input MIDI file")
    parser.add_argument("output", type=Path, help="Output MusicXML file")
    parser.add_argument("--title", required=True, help="Work and movement title")
    parser.add_argument("--composer", help="Composer credit")
    parser.add_argument("--arranger", help="Arranger credit")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file when it already exists",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.input.is_file():
        print(f"Input MIDI not found: {args.input}", file=sys.stderr)
        return 2
    if args.output.exists() and not args.force:
        print(
            f"Output already exists: {args.output}. Pass --force to overwrite.",
            file=sys.stderr,
        )
        return 2

    try:
        from music21 import converter, metadata
    except ImportError:
        print(
            "music21 is not installed. Run this script with: "
            "uv run --no-project --with music21 python "
            "scripts/midi_to_musicxml.py ...",
            file=sys.stderr,
        )
        return 2

    score = converter.parse(str(args.input), format="midi")
    if not score.parts or not score.flatten().notes:
        print("The MIDI did not produce a non-empty score.", file=sys.stderr)
        return 1

    score.metadata = metadata.Metadata()
    score.metadata.title = args.title
    if args.composer:
        score.metadata.composer = args.composer
    if args.arranger:
        score.metadata.addContributor(
            metadata.Contributor(name=args.arranger, role="arranger")
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    score.write("musicxml", fp=str(args.output))

    check = converter.parse(str(args.output), format="musicxml")
    if not check.parts or not check.flatten().notes:
        print("MusicXML validation failed after writing.", file=sys.stderr)
        return 1

    result = {
        "input": str(args.input),
        "output": str(args.output),
        "parts": len(check.parts),
        "musicxml_notes": len(check.flatten().notes),
        "title": args.title,
        "composer": args.composer,
        "arranger": args.arranger,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
