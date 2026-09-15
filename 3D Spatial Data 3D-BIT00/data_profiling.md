# Data Profiling Summary

## 1. Project overview
This project contains a local sample of Hong Kong 3D-BIT00 spatial dataset. The metadata is stored in [b1000_Tile_Apr2026_gdb_b1000_Tile_converted.geojson](b1000_Tile_Apr2026_gdb_b1000_Tile_converted.geojson), and the downloaded test files are stored under [download](download).

The dataset is a tile-based 3D urban model reference set. Each tile has a sheet code such as `13-SE-11B` and `13-SE-12A`, and each tile exposes downloadable links in several formats, including `Format_3DS`, `Format_FBX`, `Format_MAX`, and `Format_VRML`.

## 2. Data source and acquisition
The source URLs identified in the metadata point to the official Hong Kong map download API:

- `https://download.map.gov.hk/api/3d-zip/FBX3DBIT00/...`

This indicates the local files are not arbitrary uploads; they are official 3D tile downloads for the 3D-BIT00 product.

## 3. File type and meaning
The downloaded test files are FBX-based 3D model packages. The observed file types in the download directory are:

- `.fbx`: 3D geometry model file
- `.jpg`: texture or image texture file used by the model
- `.att`: attribute/metadata sidecar file associated with the model

The observed layout is:

- [download/13-SE-11B_FBX/13SE11B/T08250030000106E1B/T08250030000106E1B.fbx](download/13-SE-11B_FBX/13SE11B/T08250030000106E1B/T08250030000106E1B.fbx)
- [download/13-SE-11B_FBX/13SE11B/T08250030000106E1B/T08250030000106E1B.jpg](download/13-SE-11B_FBX/13SE11B/T08250030000106E1B/T08250030000106E1B.jpg)
- [download/13-SE-11B_FBX/13SE11B/T08250030000106E1B/T08250030000106E1B.att](download/13-SE-11B_FBX/13SE11B/T08250030000106E1B/T08250030000106E1B.att)

and similarly for the neighboring tile:

- [download/13-SE-12A_FBX/13SE12A/T09000030000106E1B/T09000030000106E1B.fbx](download/13-SE-12A_FBX/13SE12A/T09000030000106E1B/T09000030000106E1B.fbx)
- [download/13-SE-12A_FBX/13SE12A/T09000030000106E1B/T09000030000106E1B.jpg](download/13-SE-12A_FBX/13SE12A/T09000030000106E1B/T09000030000106E1B.jpg)
- [download/13-SE-12A_FBX/13SE12A/T09000030000106E1B/T09000030000106E1B.att](download/13-SE-12A_FBX/13SE12A/T09000030000106E1B/T09000030000106E1B.att)

These indicate that the downloaded archive is a textured 3D model tile: geometry + image texture + auxiliary metadata.

## 4. Dataset structure
The metadata file groups each tile as a GeoJSON feature, and each feature contains:

- `OBJECTID`
- `SHEETNO`
- `Min_x`, `Min_y`, `Max_x`, `Max_y`
- `Format_3DS`
- `Format_FBX`
- `Format_MAX`
- `Format_VRML`
- `REVISIONDATE`
- `REMARKS`

This means the dataset is a tiled index of 3D grid cells. Each tile is a polygon with geographic bounds and one or more downloadable model packages.

## 5. Downloaded sample inventory
The local download test was run for two adjacent tiles:

- `13-SE-11B`
- `13-SE-12A`

Observed file counts:

- Total files: 6
- File types: 2 FBX + 2 JPG + 2 ATT
- Total size: 1,969,523 bytes (~1.88 MB)

Size details:

| File | Size (bytes) |
|---|---:|
| 13-SE-11B FBX | 356,704 |
| 13-SE-11B JPG | 517,164 |
| 13-SE-11B ATT | 139 |
| 13-SE-12A FBX | 540,960 |
| 13-SE-12A JPG | 554,417 |
| 13-SE-12A ATT | 139 |

## 6. Data quality and status
The local smoke test shows that the download pipeline is working for the selected adjacent tiles:

- Metadata lookup succeeded
- Official URL responded successfully
- Files were downloaded into the designated download folder
- Two neighboring tiles were successfully retrieved

Current status: the sample dataset is valid and complete for the tested subset.

## 7. Interpretation
This is not a raster or vector GIS layer in the usual sense; it is a 3D model dataset packaged by tile. Each tile contains a 3D scene representation plus texture/image assets. The FBX format is especially useful for 3D authoring and visualization workflows, while the JPG file provides visual surface texture and the ATT file likely contains metadata or attribute support.

## 8. Recommended next steps
For a production-scale download, the next stage would be:

1. Expand the download script to iterate through all sheet IDs in the metadata index.
2. Optionally download multiple formats (FBX, MAX, VRML, 3DS) in parallel with a format selector.
3. Validate file counts, sizes, and checksums after full download.
4. Convert or visualize the FBX tiles in a GIS/3D engine when needed.

## 9. Conclusion
The downloaded local data is a valid subset of the Hong Kong 3D-BIT00 dataset, specifically adjacent FBX tiles for 13-SE-11B and 13-SE-12A. The files are textured 3D model assets, and the local folder shows a consistent, structured tile-based archive layout suited for downstream 3D visualization or spatial data processing.
