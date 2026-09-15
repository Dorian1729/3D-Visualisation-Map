 # 3D Photo-realistic Model Data Profiling

Last updated for handover: 2026-06-06

## 1. Project Summary

This folder contains the index data and download tooling for the Hong Kong **3D Photo-realistic Model** dataset published through the Hong Kong CSDI Portal.

The local files are not the full 3D model payloads themselves. They are spatial index files. Each index feature represents one model tile and contains:

- tile identifier
- tile boundary
- location name
- HK1980 grid coordinate range
- WGS84 longitude/latitude range
- direct download URLs for OBJ, OSGB, and Cesium model packages

The current downloader uses this index to download the actual model zip files tile by tile.

## 2. Official Data Source

Primary source:

- CSDI Portal dataset page: <https://portal.csdi.gov.hk/csdi-webpage/dataset/pland_rcd_1636534828693_9849>
- CSDI metadata panel entry point used during profiling: <https://portal.csdi.gov.hk/geoportal/#metadataInfoPanel>
- Planning Department notes PDF: <https://www.pland.gov.hk/pland_en/info_serv/3D_models/Remarks_for_the_3D_Photo-realistic_Model.pdf>

Official dataset name:

- English: `3D Photo-realistic Model`
- Traditional Chinese and Simplified Chinese names are available on the CSDI dataset page.

Publishing organisation:

- Planning Department, HKSAR Government

CSDI category:

- Development

Official description summary:

- The Planning Department prepared a 3D photo-realistic model for part of Hong Kong Island and Kowloon Peninsula.
- The Hong Kong Island part was produced from aerial photographs captured in March 2017.
- The Kowloon Peninsula part was produced from aerial photographs captured in March 2018.
- The data is provided for reference only. Users should assess fitness for their own use.
- The Planning Department states that it does not undertake to provide updated versions and may suspend the data provision.

The Planning Department notes PDF states the model download pattern as:

```text
https://pdmap.pland.gov.hk/PLANDWEB/public/3d_photo_realistic_models/<FORMAT>/<GRID_NAME>_<FORMAT>.zip
```

In the local GeoJSON, the direct URLs are already materialised in `OSGB_URL`, `OBJ_URL`, and `Cesium_URL`, so the script does not need to reconstruct them manually.

## 3. Local Folder Contents

Current project path used during profiling:

```text
D:\...\3D Visualisation Map\3D Photo-realistic Model
```

Important local files:

```text
OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson
full_download_models.py
DATA_PROFILING.md
```

Format-specific index folders:

```text
3D_Photo_realistic_Model_GEOJSON
3D_Photo_realistic_Model_GEOPACKAGE
3D_Photo_realistic_Model_GML
3D_Photo_realistic_Model_KML
3D_Photo_realistic_Model_SHP
3D_Photo_realistic_Model_FGDB
```

The same tile index is available in multiple GIS formats:

| Folder | Format | Main use |
|---|---|---|
| `3D_Photo_realistic_Model_GEOJSON` | GeoJSON | Best for scripting and web/GIS processing |
| `3D_Photo_realistic_Model_SHP` | Esri Shapefile | QGIS / ArcGIS desktop workflows |
| `3D_Photo_realistic_Model_GEOPACKAGE` | GeoPackage | Single-file GIS database, QGIS/ArcGIS friendly |
| `3D_Photo_realistic_Model_GML` | GML + XSD | Standards-based exchange format |
| `3D_Photo_realistic_Model_KML` | KML | Google Earth / KML viewers |
| `3D_Photo_realistic_Model_FGDB` | Esri File Geodatabase | ArcGIS geodatabase format |

Recommended script input:

```text
OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson
```

or:

```text
3D_Photo_realistic_Model_GEOJSON\OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson
```

The downloader expects the GeoJSON file to be in the same folder as `full_download_models.py` by default.

## 4. Dataset Profile

Profiled local GeoJSON:

```text
3D_Photo_realistic_Model_GEOJSON\OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson
```

Feature count:

```text
2150 tiles
```

Available model links:

| Link field | Count | Package type |
|---|---:|---|
| `OBJ_URL` | 2150 | OBJ zip |
| `OSGB_URL` | 2150 | OSGB zip |
| `Cesium_URL` | 2150 | Cesium / 3D Tiles zip |

Coordinate extent from the local index:

| Field | Minimum | Maximum | Meaning |
|---|---:|---:|---|
| `MIN_X` | 830000 | 844250 | west edge in Hong Kong 1980 Grid |
| `MIN_Y` | 809000 | 823711 | south edge in Hong Kong 1980 Grid |
| `MAX_X` | 830250 | 844500 | east edge in Hong Kong 1980 Grid |
| `MAX_Y` | 809250 | 823742 | north edge in Hong Kong 1980 Grid |
| `MIN_LNG` | 114.11605316 | 114.254316038 | minimum longitude, WGS84 |
| `MIN_LAT` | 22.2196610051 | 22.3525158889 | minimum latitude, WGS84 |
| `MAX_LNG` | 114.118479957 | 114.256742828 | maximum longitude, WGS84 |
| `MAX_LAT` | 22.2219192388 | 22.3527966178 | maximum latitude, WGS84 |

The tiles are typically about 250 m by 250 m in HK1980 grid coordinates.

Location groups found in the index:

- Aberdeen to Repulse Bay
- Causeway Bay
- Chai Wan to Shek O
- Kowloon Bay, Kai Tak (East), Choi Hung, Diamond Hill and Tsz Wan Shan
- Kwun Tong, Ngau Tau Kok, and Cha Kwo Ling
- Mong Kok, Yau Ma Tei, Jordon and Tai Kok Tsui
- North Point
- Sheung Wan to Pok Fu Lam
- Tai Kok Tsui, Sham Shui Po, Cheung Sha Wan, Kowloon Tong, and Prince Edward
- To Kwa Wan, Kowloon City, Wong Tai Sin, Kai Tak (West)
- Wan Chai, Admiralty and Central
- West Kowloon, Hung Hom
- Yau Tong, Lam Tin, Sau Mau Ping, Anderson Road and Ma Yau Tong

## 5. Field Dictionary

The following fields are present in the local GeoJSON:

| Field | Type | Meaning |
|---|---|---|
| `GRID_NAME` | text | tile identifier / index grid name |
| `LOC_EN` | text | location name in English |
| `LOC_TC` | text | location name in Traditional Chinese |
| `LOC_SC` | text | location name in Simplified Chinese |
| `MIN_X` | number | west edge coordinate in Hong Kong 1980 Grid |
| `MIN_Y` | number | south edge coordinate in Hong Kong 1980 Grid |
| `MAX_X` | number | east edge coordinate in Hong Kong 1980 Grid |
| `MAX_Y` | number | north edge coordinate in Hong Kong 1980 Grid |
| `MIN_LNG` | number | minimum longitude in WGS84 |
| `MIN_LAT` | number | minimum latitude in WGS84 |
| `MAX_LNG` | number | maximum longitude in WGS84 |
| `MAX_LAT` | number | maximum latitude in WGS84 |
| `MODI_DATE` | date-like text/integer | modification date |
| `OSGB_URL` | text | direct URL to OSGB zip package |
| `OBJ_URL` | text | direct URL to OBJ zip package |
| `Cesium_URL` | text | direct URL to Cesium / 3D Tiles zip package |
| `Shape_Leng` | number | polygon perimeter from GIS export |
| `Shape_Area` | number | polygon area from GIS export |

Sample tile:

```text
GRID_NAME: Tile_+005_+006
LOC_EN: Mong Kok, Yau Ma Tei, Jordon and Tai Kok Tsui
MIN_X / MIN_Y / MAX_X / MAX_Y: 834872 / 818398 / 835122 / 818648
MIN_LNG / MIN_LAT / MAX_LNG / MAX_LAT: 114.163302 / 22.304511 / 114.165772 / 22.306809
MODI_DATE: 20190128
OBJ_URL: https://pdmap.pland.gov.hk/PLANDWEB/public/3d_photo_realistic_models/obj/Tile_+005_+006_OBJ.zip
OSGB_URL: https://pdmap.pland.gov.hk/PLANDWEB/public/3d_photo_realistic_models/osgb/Tile_+005_+006_OSGB.zip
Cesium_URL: https://pdmap.pland.gov.hk/PLANDWEB/public/3d_photo_realistic_models/Cesium/Tile_+005_+006_Cesium.zip
```

## 6. Downloadable Model Package Types

Each tile has three downloadable package options.

### OBJ

URL field:

```text
OBJ_URL
```

Typical zip name:

```text
Tile_+005_+006_OBJ.zip
```

Typical extracted structure:

```text
Tile_+005_+006/
  Tile_+005_+006.obj
  Tile_+005_+006.mtl
  Tile_+005_+006_0.jpg
```

Use cases:

- Blender import
- Mesh inspection
- General 3D modelling workflows

Validated behaviour:

- Adjacent OBJ tiles share a common local coordinate system.
- `Tile_+005_+006` and `Tile_+006_+006` were tested in Blender and stitched correctly without manual translation.
- OBJ coordinates are not HK1980 absolute coordinates. They use a local engineering coordinate system, but neighbouring tiles are consistently placed relative to each other.

### OSGB

URL field:

```text
OSGB_URL
```

Typical zip name:

```text
Tile_+005_+006_OSGB.zip
```

Use cases:

- GIS / 3D engines that support OSGB
- Some photogrammetry and 3D city model workflows

The Planning Department notes indicate OSGB packages may contain `.osgb` files and related model/data subfolders, depending on area/package.

### Cesium / 3D Tiles

URL field:

```text
Cesium_URL
```

Typical zip name:

```text
Tile_+005_+006_Cesium.zip
```

Use cases:

- CesiumJS
- Web 3D map viewers
- 3D Tiles workflows

The Planning Department notes indicate Cesium packages contain 3D Tiles resources such as tileset JSON files and `.b3dm` content.

## 7. Download Script

Script:

```text
full_download_models.py
```

Purpose:

- Read the GeoJSON tile index.
- Create download tasks from `OBJ_URL`, `OSGB_URL`, and/or `Cesium_URL`.
- Download zip files into a structured folder.
- Skip existing valid zip files.
- Validate zip integrity.
- Write a CSV report.

The script uses only Python standard library modules. No external Python packages are required.

Expected placement:

```text
some_folder/
  full_download_models.py
  OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson
```

Default output behaviour:

- The script first tries to create/use a folder named `download` next to `full_download_models.py`.
- If `download` already exists and has content, the script creates a new timestamped folder such as:

```text
download_20260606_112233
```

Default output structure:

```text
download/
  Tile_+005_+006/
    obj/
      Tile_+005_+006_OBJ.zip
  Tile_+006_+006/
    obj/
      Tile_+006_+006_OBJ.zip
  download_report.csv
```

For all formats:

```text
download/
  Tile_+005_+006/
    obj/
      Tile_+005_+006_OBJ.zip
    osgb/
      Tile_+005_+006_OSGB.zip
    cesium/
      Tile_+005_+006_Cesium.zip
```

## 8. Quick Start

Open PowerShell in the folder containing `full_download_models.py`, then run:

```powershell
python full_download_models.py --dry-run
```

Expected default task count for OBJ:

```text
2150 file(s), formats=obj
```

Download all OBJ packages:

```powershell
python full_download_models.py
```

Recommended safer full download with lower concurrency:

```powershell
python full_download_models.py --workers 2
```

Download a few specific tiles:

```powershell
python full_download_models.py --tile "Tile_+005_+006" --tile "Tile_+006_+006"
```

Download all three formats:

```powershell
python full_download_models.py --format all --workers 2
```

Use a custom output folder:

```powershell
python full_download_models.py --output "E:\3D Photo-realistic Model\download"
```

Use a custom GeoJSON path:

```powershell
python full_download_models.py --geojson "D:\path\to\OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson"
```

## 9. Script Options

| Option | Default | Meaning |
|---|---|---|
| `--geojson` | same folder as script | GeoJSON index file |
| `--output` | auto-selected `download` folder | download target directory |
| `--report` | `<output>\download_report.csv` | CSV report path |
| `--format` | `obj` | one of `obj`, `osgb`, `cesium`, `all` |
| `--tile` | none | restrict to selected `GRID_NAME`; can be repeated |
| `--tile-file` | none | text file with one `GRID_NAME` per line |
| `--workers` | `3` | concurrent download threads |
| `--retries` | `3` | retry count per file |
| `--timeout` | `120` seconds | HTTP timeout |
| `--dry-run` | false | show planned tasks without downloading |
| `--no-validate` | false | skip zip integrity validation |

## 10. Download Logic

The downloader follows this process:

1. Resolve `BASE_DIR` from the location of `full_download_models.py`.
2. Load the GeoJSON index.
3. Choose the output directory:
   - use/create `download` if it does not exist or is empty;
   - create `download_<timestamp>` if `download` already has content.
4. Build download tasks:
   - default: all `OBJ_URL` values;
   - optional: OSGB, Cesium, or all formats;
   - optional: restrict by tile list.
5. For each task, build a destination path:

```text
<output>/<GRID_NAME>/<format>/<zip filename>
```

6. Skip existing non-empty files after zip validation.
7. Download missing files using HTTP GET.
8. Write into a `.part` temporary file first.
9. Rename `.part` to `.zip` only after the HTTP request finishes.
10. Validate downloaded zip files with Python `zipfile.testzip()`.
11. Write a CSV report with status, bytes, destination, URL, and message.

Possible statuses in `download_report.csv`:

| Status | Meaning |
|---|---|
| `downloaded` | file was downloaded and validated |
| `skipped` | existing file was present and valid |
| `failed` | request failed after retries |
| `invalid_download` | downloaded file was not a valid zip |
| `invalid_existing` | existing file failed zip validation |

## 11. Blender Notes

OBJ is the recommended format for Blender.

Import process:

1. Extract the OBJ zip.
2. In Blender, use:

```text
File > Import > Wavefront (.obj)
```

3. Select the `.obj` file, not the `.jpg`.
4. Keep `.obj`, `.mtl`, and `.jpg` in the same folder.
5. Use Material Preview or Rendered view to see textures.

Important observations from profiling:

- `Tile_+005_+006` contains roughly 340k vertices and 675k faces.
- Adjacent tile test: `Tile_+005_+006` and `Tile_+006_+006` imported into Blender and aligned successfully.
- Full dataset import is likely limited by Blender/GPU/RAM performance, not by coordinate mismatch.
- Avoid importing all 2150 OBJ tiles at once unless the workstation has enough memory and GPU capacity.
- Recommended workflow is to import by area or by selected tile ranges.

## 12. Known Risks and Operational Notes

- The full OBJ download is large. A single tile can be tens to over one hundred MB.
- All three formats multiply the download volume significantly.
- Server availability and download speed depend on the current network environment.
- The Planning Department disclaimer says the data is for reference and may be modified, suspended, or not updated.
- If a download is interrupted, rerun the script. Valid existing zip files are skipped.
- If a zip is corrupted, delete that zip or rerun with a fresh output folder.
- Keep the GeoJSON index with the script when transferring the project to another computer.

## 13. Handover Checklist

Before handing this project to another person, include:

- `full_download_models.py`
- `OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson`
- this `DATA_PROFILING.md`
- optional GIS source folders if desktop GIS inspection is needed:
  - `3D_Photo_realistic_Model_GEOJSON`
  - `3D_Photo_realistic_Model_SHP`
  - `3D_Photo_realistic_Model_GEOPACKAGE`
  - `3D_Photo_realistic_Model_GML`
  - `3D_Photo_realistic_Model_KML`
  - `3D_Photo_realistic_Model_FGDB`

Minimum runnable package:

```text
3D Photo-realistic Model/
  full_download_models.py
  OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson
  DATA_PROFILING.md
```

Then run:

```powershell
python full_download_models.py --dry-run
python full_download_models.py --workers 2
```

## 14. Source Links

- CSDI dataset page: <https://portal.csdi.gov.hk/csdi-webpage/dataset/pland_rcd_1636534828693_9849>
- CSDI metadata panel: <https://portal.csdi.gov.hk/geoportal/#metadataInfoPanel>
- Planning Department model notes: <https://www.pland.gov.hk/pland_en/info_serv/3D_models/Remarks_for_the_3D_Photo-realistic_Model.pdf>
- Kowloon metadata archive referenced by CSDI: <https://www.pland.gov.hk/pland_tc/info_serv/3D_models/Metadata/KLN_metadata.zip>
