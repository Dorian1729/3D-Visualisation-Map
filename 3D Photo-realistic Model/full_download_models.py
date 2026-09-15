#!/usr/bin/env python3
"""
Full downloader for the Hong Kong 3D photo-realistic model index.

Place this script next to:
  OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson

Default output:
  ./download/<GRID_NAME>/<format>/<zip file>

If ./download already exists and is not empty, the script creates a new
timestamped output folder next to it.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_GEOJSON = BASE_DIR / "OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson"
DEFAULT_OUTPUT = BASE_DIR / "download"
REPORT_FILENAME = "download_report.csv"

FORMAT_TO_FIELD = {
    "obj": "OBJ_URL",
    "osgb": "OSGB_URL",
    "cesium": "Cesium_URL",
}

print_lock = threading.Lock()


@dataclass(frozen=True)
class DownloadTask:
    grid_name: str
    model_format: str
    url: str
    destination: Path


@dataclass(frozen=True)
class DownloadResult:
    task: DownloadTask
    status: str
    message: str
    bytes_written: int


def log(message: str) -> None:
    with print_lock:
        print(message, flush=True)


def load_features(geojson_path: Path) -> list[dict]:
    with geojson_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    features = data.get("features", [])
    if not isinstance(features, list):
        raise ValueError("GeoJSON does not contain a features array.")
    return features


def filename_from_url(url: str) -> str:
    path = unquote(urlparse(url).path)
    name = Path(path).name
    if not name:
        raise ValueError(f"Cannot infer file name from URL: {url}")
    return name


def load_tile_filter(tile_file: Path | None, tiles: list[str] | None) -> set[str] | None:
    selected = set(tiles or [])
    if tile_file:
        for line in tile_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                selected.add(line)
    return selected or None


def build_tasks(
    features: list[dict],
    output_dir: Path,
    formats: list[str],
    selected_tiles: set[str] | None,
) -> list[DownloadTask]:
    tasks: list[DownloadTask] = []
    seen: set[tuple[str, str]] = set()

    for feature in features:
        properties = feature.get("properties") or {}
        grid_name = properties.get("GRID_NAME")
        if not grid_name:
            continue
        if selected_tiles is not None and grid_name not in selected_tiles:
            continue

        for model_format in formats:
            field = FORMAT_TO_FIELD[model_format]
            url = properties.get(field)
            if not url:
                continue
            key = (grid_name, model_format)
            if key in seen:
                continue
            seen.add(key)
            destination = output_dir / grid_name / model_format / filename_from_url(url)
            tasks.append(DownloadTask(grid_name, model_format, url, destination))

    return tasks


def directory_has_content(path: Path) -> bool:
    return path.exists() and any(path.iterdir())


def choose_default_output_dir(base_output_dir: Path) -> Path:
    if not base_output_dir.exists():
        base_output_dir.mkdir(parents=True)
        return base_output_dir

    if not directory_has_content(base_output_dir):
        return base_output_dir

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parent = base_output_dir.parent
    stem = base_output_dir.name
    candidate = parent / f"{stem}_{timestamp}"
    counter = 2
    while candidate.exists():
        candidate = parent / f"{stem}_{timestamp}_{counter}"
        counter += 1

    candidate.mkdir(parents=True)
    return candidate


def validate_zip(zip_path: Path) -> tuple[bool, str]:
    if not zip_path.exists() or zip_path.stat().st_size == 0:
        return False, "missing or empty file"
    try:
        with zipfile.ZipFile(zip_path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                return False, f"corrupted zip member: {bad_member}"
            file_count = sum(1 for item in archive.infolist() if not item.is_dir())
            return True, f"zip OK, files={file_count}"
    except zipfile.BadZipFile as error:
        return False, f"bad zip: {error}"


def download_one(task: DownloadTask, retries: int, timeout: int, validate: bool) -> DownloadResult:
    if task.destination.exists() and task.destination.stat().st_size > 0:
        if validate:
            ok, message = validate_zip(task.destination)
            status = "skipped" if ok else "invalid_existing"
            return DownloadResult(task, status, message, task.destination.stat().st_size)
        return DownloadResult(task, "skipped", "existing file", task.destination.stat().st_size)

    task.destination.parent.mkdir(parents=True, exist_ok=True)
    temp_destination = task.destination.with_suffix(task.destination.suffix + ".part")

    for attempt in range(1, retries + 1):
        try:
            request = Request(task.url, headers={"User-Agent": "full-model-downloader/1.0"})
            with urlopen(request, timeout=timeout) as response:
                with temp_destination.open("wb") as file:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        file.write(chunk)

            temp_destination.replace(task.destination)
            bytes_written = task.destination.stat().st_size
            if validate:
                ok, message = validate_zip(task.destination)
                if not ok:
                    return DownloadResult(task, "invalid_download", message, bytes_written)
                return DownloadResult(task, "downloaded", message, bytes_written)
            return DownloadResult(task, "downloaded", "download OK", bytes_written)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            if attempt < retries:
                time.sleep(min(30, 2 * attempt))
                continue
            return DownloadResult(task, "failed", str(error), 0)

    return DownloadResult(task, "failed", "unknown failure", 0)


def write_report(report_path: Path, results: list[DownloadResult]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "time",
                "grid_name",
                "format",
                "status",
                "bytes",
                "destination",
                "url",
                "message",
            ]
        )
        now = datetime.now().isoformat(timespec="seconds")
        for result in results:
            writer.writerow(
                [
                    now,
                    result.task.grid_name,
                    result.task.model_format,
                    result.status,
                    result.bytes_written,
                    result.task.destination,
                    result.task.url,
                    result.message,
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download all selected 3D photo-realistic model zip files."
    )
    parser.add_argument("--geojson", type=Path, default=DEFAULT_GEOJSON)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Optional custom download directory. If omitted, the script creates "
            "or uses ./download next to this script; if ./download is non-empty, "
            "it creates a new timestamped folder."
        ),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional CSV report path. Default: <actual output folder>/download_report.csv.",
    )
    parser.add_argument(
        "--format",
        choices=["obj", "osgb", "cesium", "all"],
        default="obj",
        help="Format to download. Default: obj. Use all for OBJ, OSGB, and Cesium.",
    )
    parser.add_argument(
        "--tile",
        action="append",
        default=None,
        help="Limit to one GRID_NAME. Repeat for multiple tiles.",
    )
    parser.add_argument(
        "--tile-file",
        type=Path,
        default=None,
        help="Optional text file with one GRID_NAME per line.",
    )
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the planned tasks; do not download.",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip zip integrity validation after download and for existing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.workers < 1:
        print("--workers must be at least 1", file=sys.stderr)
        return 2

    output_dir = args.output or choose_default_output_dir(DEFAULT_OUTPUT)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report or (output_dir / REPORT_FILENAME)

    features = load_features(args.geojson)
    formats = list(FORMAT_TO_FIELD) if args.format == "all" else [args.format]
    selected_tiles = load_tile_filter(args.tile_file, args.tile)
    tasks = build_tasks(features, output_dir, formats, selected_tiles)

    print(f"GeoJSON: {args.geojson}")
    print(f"Output:  {output_dir}")
    print(f"Report:  {report_path}")
    print(f"Tasks:   {len(tasks)} file(s), formats={','.join(formats)}")

    if not tasks:
        print("No download tasks found.")
        return 1

    if args.dry_run:
        for task in tasks[:20]:
            print(f"DRY {task.grid_name} {task.model_format} -> {task.destination.name}")
        if len(tasks) > 20:
            print(f"... {len(tasks) - 20} more task(s)")
        return 0

    results: list[DownloadResult] = []
    validate = not args.no_validate
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_task = {
            executor.submit(download_one, task, args.retries, args.timeout, validate): task
            for task in tasks
        }
        completed = 0
        for future in as_completed(future_to_task):
            completed += 1
            result = future.result()
            results.append(result)
            log(
                f"[{completed}/{len(tasks)}] {result.status}: "
                f"{result.task.grid_name} {result.task.model_format} "
                f"{result.bytes_written} bytes ({result.message})"
            )

    write_report(report_path, results)

    failed = [result for result in results if result.status in {"failed", "invalid_download", "invalid_existing"}]
    downloaded = sum(1 for result in results if result.status == "downloaded")
    skipped = sum(1 for result in results if result.status == "skipped")
    print(f"Done. downloaded={downloaded}, skipped={skipped}, failed_or_invalid={len(failed)}")
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
