#!/usr/bin/env python3
"""Download 3D-BIT00 tiles from the official Hong Kong map download API.

The source metadata is stored in the GeoJSON file in this workspace, where each tile
contains properties like "Format_3DS", "Format_FBX", "Format_MAX", and "Format_VRML".

Examples:
  python download_3d_bit00.py --format FBX --dry-run
  python download_3d_bit00.py --format VRML --sheetno "13-SE-11B"
  python download_3d_bit00.py --format all --limit 10
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable, List, Dict, Any, Tuple

DEFAULT_GEOJSON = "b1000_Tile_Apr2026_gdb_b1000_Tile_converted.geojson"
SUPPORTED_FORMATS = {"3DS", "FBX", "MAX", "VRML"}


def load_feature_records(geojson_path: str) -> List[Dict[str, str]]:
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records: List[Dict[str, str]] = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        sheetno = str(props.get("SHEETNO", "")).strip()
        for key, value in props.items():
            if not key.startswith("Format_"):
                continue
            format_name = key.replace("Format_", "", 1)
            if format_name.upper() not in SUPPORTED_FORMATS:
                continue
            if not value:
                continue
            records.append({
                "sheetno": sheetno,
                "format": format_name.upper(),
                "url": value,
            })
    return records


def filter_records(records: Iterable[Dict[str, str]], format_name: str | None, sheetno: str | None) -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    for record in records:
        format_ok = True
        sheet_ok = True

        if format_name:
            target = format_name.upper()
            if target != "ALL" and record["format"] != target:
                format_ok = False

        if sheetno:
            if record["sheetno"].upper() != sheetno.upper():
                sheet_ok = False

        if format_ok and sheet_ok:
            result.append(record)
    return result


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_filename(name: str) -> str:
    invalid_chars = "\\/:*?\"<>|\r\n"
    for ch in invalid_chars:
        name = name.replace(ch, "_")
    return name.strip().strip(".") or "download"


def download_file(url: str, target_path: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
            "Accept": "*/*",
        })
        with urllib.request.urlopen(req, timeout=60) as r, open(target_path, "wb") as f:
            while True:
                chunk = r.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
        return True
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {url}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[ERROR] {url} -> {e}", file=sys.stderr)
        return False


def build_output_path(output_dir: Path, sheetno: str, format_name: str, url: str) -> Path:
    safe_sheet = safe_filename(sheetno or "unknown_sheet")
    safe_format = safe_filename(format_name)
    basename = os.path.basename(url.split("?", 1)[0])
    if not basename:
        basename = f"{safe_sheet}_{safe_format}.zip"
    return output_dir / safe_format / f"{safe_sheet}_{basename}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download 3D-BIT00 zip files from the official HK map download URLs.")
    parser.add_argument("--geojson", default=DEFAULT_GEOJSON, help="Path to the GeoJSON metadata file.")
    parser.add_argument("--out-dir", default="download", help="Directory to save downloaded zip files.")
    parser.add_argument("--format", default="FBX", choices=["ALL", "3DS", "FBX", "MAX", "VRML"], help="Download format to use.")
    parser.add_argument("--sheetno", default=None, help="Optional sheet code filter, example: 13-SE-11B")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of files to download.")
    parser.add_argument("--dry-run", action="store_true", help="Only list the download tasks without fetching files.")
    parser.add_argument("--skip-existing", action="store_true", help="Skip files already present on disk.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    geojson_path = Path(args.geojson)
    if not geojson_path.exists():
        print(f"GeoJSON file not found: {geojson_path}", file=sys.stderr)
        return 2

    records = load_feature_records(str(geojson_path))
    filtered = filter_records(records, args.format, args.sheetno)

    if args.limit is not None:
        filtered = filtered[: args.limit]

    if not filtered:
        print("No records matched the selected format / sheet filter.", file=sys.stderr)
        return 1

    print(f"Matched {len(filtered)} file(s).")
    for item in filtered:
        print(f"- {item['sheetno']} [{item['format']}] -> {item['url']}")

    if args.dry_run:
        print("Dry run enabled; no files were downloaded.")
        return 0

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = Path(__file__).resolve().parent / out_dir
    ensure_dir(out_dir)
    success_count = 0
    fail_count = 0

    for item in filtered:
        target = build_output_path(out_dir, item["sheetno"], item["format"], item["url"])
        if args.skip_existing and target.exists():
            print(f"[skip] {target.name}")
            continue

        ensure_dir(target.parent)
        print(f"[download] {item['sheetno']} [{item['format']}] -> {target.name}")
        ok = download_file(item["url"], target)
        if ok:
            success_count += 1
        else:
            fail_count += 1

    print(f"Done. Success: {success_count}, Failed: {fail_count}, Output: {out_dir}")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
