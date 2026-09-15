#!/usr/bin/env python3
"""Download a small test set of two adjacent 3D-BIT00 tiles into the download folder.

This is intended as a smoke test: it downloads only two neighboring tile URLs
from the metadata and saves them under ./download/
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

GEOJSON = "b1000_Tile_Apr2026_gdb_b1000_Tile_converted.geojson"
OUTPUT_DIR = Path(__file__).resolve().parent / "download"
FORMAT = "FBX"
TARGET_SHEETS = ["13-SE-11B", "13-SE-12A"]


def load_lookup():
    meta_path = Path(__file__).resolve().parent / GEOJSON
    with meta_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    lookup = {}
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        sheet = str(props.get("SHEETNO", "")).strip()
        url = props.get(f"Format_{FORMAT}")
        if sheet and url:
            lookup[sheet.upper()] = url
    return lookup


def download_file(url: str, output_path: Path) -> bool:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
                "Accept": "*/*",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp, output_path.open("wb") as f:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
        return output_path.exists() and output_path.stat().st_size > 0
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {url}", file=sys.stderr)
        return False
    except Exception as exc:
        print(f"[ERROR] {url} -> {exc}", file=sys.stderr)
        return False


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lookup = load_lookup()

    print(f"Using metadata: {GEOJSON}")
    print(f"Output folder: {OUTPUT_DIR}")

    missing = []
    for sheet in TARGET_SHEETS:
        if sheet.upper() not in lookup:
            missing.append(sheet)

    if missing:
        print(f"Missing metadata for: {missing}", file=sys.stderr)
        return 2

    success = 0
    for sheet in TARGET_SHEETS:
        url = lookup[sheet.upper()]
        safe_name = f"{sheet}_{FORMAT}.zip"
        target = OUTPUT_DIR / safe_name
        print(f"Downloading {sheet} -> {target.name}")
        ok = download_file(url, target)
        if ok:
            success += 1
            print(f"[OK] {target} ({target.stat().st_size} bytes)")
        else:
            print(f"[FAIL] {sheet} {target}")

    print(f"Finished: {success}/{len(TARGET_SHEETS)} downloaded successfully")
    return 0 if success == len(TARGET_SHEETS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
