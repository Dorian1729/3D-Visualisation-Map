#!/usr/bin/env python3
"""Download and extract exactly three adjoining Central OBJ tiles.

Python 3.10+, standard library only. Run from any working directory:
    python "3D Photo-realistic Model/download_central_obj_test.py"
    python "3D Photo-realistic Model/download_central_obj_test.py" --dry-run

Output is always download/test beside this script. Original OBJ coordinates,
MTL files, textures and config.json are preserved. Import all three OBJs with
the same axis/scale settings; do not center each tile individually.
"""

from __future__ import annotations

import argparse
import http.client
import json
import math
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
from urllib.request import Request, urlopen

BASE_DIR = Path(__file__).resolve().parent
INDEX = BASE_DIR / "OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson"
OUTPUT = BASE_DIR / "download" / "test"
# South -> north; HK1980 bounds: E 834250..834500, N 815500..816250.
TILES = ("tile_20_26", "tile_20_27", "tile_20_28")


def select_tiles(index: Path) -> list[dict]:
    data = json.loads(index.read_text(encoding="utf-8"))
    selected = []
    for name in TILES:
        matches = [f for f in data["features"]
                   if f["properties"].get("GRID_NAME") == name]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one index entry for {name}.")
        feature = matches[0]
        p = feature["properties"]
        url = urlparse(p.get("OBJ_URL", ""))
        if (url.scheme != "https" or url.hostname != "pdmap.pland.gov.hk"
                or not url.path.endswith(f"/{name}_OBJ.zip")):
            raise ValueError(f"Missing or unexpected official OBJ URL: {name}")
        if "Central" not in p.get("LOC_EN", ""):
            raise ValueError(f"Tile is not labelled as covering Central: {name}")
        if (p["MIN_X"], p["MAX_X"], p["MAX_Y"] - p["MIN_Y"]) != (834250, 834500, 250):
            raise ValueError(f"Unexpected Central tile bounds: {name}")
        selected.append(feature)
    if selected[0]["properties"]["MIN_Y"] != 815500:
        raise ValueError("Unexpected southern boundary.")
    for south, north in zip(selected, selected[1:]):
        if south["properties"]["MAX_Y"] != north["properties"]["MIN_Y"]:
            raise ValueError("Tiles do not share a full edge.")
    return selected


def inspect_zip(path: Path, tile: str) -> dict:
    """CRC-check all members and read the OBJ-to-HK1980 transform."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        for name in names:
            member = PurePosixPath(name)
            if (member.is_absolute() or ".." in member.parts or "\\" in name
                    or ":" in name or not member.parts or member.parts[0] != tile):
                raise ValueError(f"Unexpected ZIP member: {name}")
        for suffix in (".obj", ".mtl", ".jpg"):
            if not any(name.lower().endswith(suffix) for name in names):
                raise ValueError(f"{tile}: ZIP has no {suffix} file.")
        bad = archive.testzip()
        if bad:
            raise ValueError(f"CRC check failed: {bad}")
        config = json.loads(archive.read(f"{tile}/config.json"))
        matrix = config["model_transform"]
        if (len(matrix) != 4 or any(len(row) != 4 for row in matrix)
                or any(not math.isfinite(v) for row in matrix for v in row)):
            raise ValueError(f"Invalid model_transform: {tile}")
        return {
            "model_transform": matrix,
            "obj_files": [name for name in names if name.lower().endswith(".obj")],
        }


def download_tile(p: dict, output: Path, retries: int, timeout: int) -> dict:
    tile = p["GRID_NAME"]
    target = output / f"{tile}_OBJ.zip"
    if target.exists():
        # An existing invalid archive is reported instead of silently overwritten.
        info = inspect_zip(target, tile)
        print(f"[SKIP] Valid existing archive: {target.name}", flush=True)
        return info
    partial = target.with_suffix(".zip.part")
    for attempt in range(1, retries + 1):
        try:
            print(f"[GET {attempt}/{retries}] {tile}", flush=True)
            request = Request(p["OBJ_URL"], headers={"User-Agent": "central-obj-test/1.0"})
            with urlopen(request, timeout=timeout) as response, partial.open("wb") as dest:
                expected = response.headers.get("Content-Length")
                last_log = time.monotonic()
                while chunk := response.read(1024 * 1024):
                    dest.write(chunk)
                    if time.monotonic() - last_log >= 5:
                        print(f"  {tile}: {dest.tell() / 1024**2:.1f} MiB", flush=True)
                        last_log = time.monotonic()
            if expected is not None and partial.stat().st_size != int(expected):
                raise ValueError(f"Incomplete HTTP response for {tile}.")
            info = inspect_zip(partial, tile)
            partial.replace(target)
            print(f"[OK] {target.name} (CRC verified)", flush=True)
            return info
        except (OSError, ValueError, KeyError, http.client.HTTPException, zipfile.BadZipFile) as error:
            if attempt == retries:
                raise RuntimeError(f"{tile}: {error}") from error
            print(f"[RETRY] {error}", flush=True)
            time.sleep(min(2 * attempt, 10))
    raise RuntimeError(f"Download did not complete: {tile}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview only; no writes or downloads.")
    parser.add_argument("--retries", type=int, default=3, help="Maximum attempts per tile (default: 3).")
    parser.add_argument("--timeout", type=int, default=120, help="Network timeout in seconds (default: 120).")
    args = parser.parse_args()
    if args.retries < 1 or args.timeout < 1:
        parser.error("--retries and --timeout must be positive.")
    features = select_tiles(INDEX)
    print(f"Output: {OUTPUT}")
    print("Central: 3 adjoining tiles, 250 m east-west x 750 m south-north.")
    for feature in features:
        p = feature["properties"]
        print(f"  {p['GRID_NAME']}: {p['OBJ_URL']}")
    if args.dry_run:
        return 0

    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    for feature in features:
        p = feature["properties"]
        info = download_tile(p, OUTPUT, args.retries, args.timeout)
        records.append({"tile": p["GRID_NAME"], "url": p["OBJ_URL"], **info})
    # Different OBJ coordinate frames would require applying individual transforms.
    # Refuse to claim direct alignment if the upstream model packages change.
    reference = records[0]["model_transform"]
    for record in records[1:]:
        if any(abs(a - b) > 1e-8 for ra, rb in zip(reference, record["model_transform"])
               for a, b in zip(ra, rb)):
            raise ValueError("Model transforms differ; direct OBJ alignment is no longer valid.")

    for record in records:
        tile = record["tile"]
        print(f"[EXTRACT] {tile}", flush=True)
        # Each archive has its own tile directory, so identical MTL/texture names
        # from different tiles cannot overwrite one another. Extraction on rerun
        # refreshes archive members and recovers an interrupted extraction.
        with zipfile.ZipFile(OUTPUT / f"{tile}_OBJ.zip") as archive:
            archive.extractall(OUTPUT)
    manifest = {
        "tiles_south_to_north": records,
        "bounds_hk1980": [834250, 815500, 834500, 816250],
        "units": "metres",
        "alignment": "Same OBJ coordinate frame; import all tiles without individual centering.",
        "georeferencing": "HK1980 = model_transform * [OBJ_x, OBJ_y, OBJ_z, 1].",
    }
    (OUTPUT / "central_tiles.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "central_tiles.geojson").write_text(json.dumps({
        "type": "FeatureCollection", "features": features,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Done: 3 verified ZIPs and extracted OBJ/MTL/textures.")
    print("Import these together using identical axis/scale settings:")
    for record in records:
        for obj in record["obj_files"]:
            print(f"  {OUTPUT / obj}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted. Rerun to skip valid ZIPs; partial files restart from zero.", file=sys.stderr)
        sys.exit(130)
