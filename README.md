# 香港三维地图数据项目

本项目整理了五套香港三维地图产品的空间索引和 Python 下载脚本，用于理解数据来源、按图幅获取模型，以及后续三维可视化处理。各 `download` 目录的内容已由 `.gitignore` 排除（保留 `.gitkeep` 占位文件），本 README 不介绍其中的文件、容量或下载进度。

**理解项目的关键是区分三个层次：地图产品、索引保存格式、模型下载格式。**

- **地图产品**：例如单体化模型、无纹理模型、实景模型，决定数据表达什么。
- **索引保存格式**：例如 GeoJSON、GeoPackage、GML，记录分块位置、编号、更新时间和下载链接。
- **模型下载格式**：例如 OBJ、FBX、OSGB，决定实际三维数据以什么方式交付。

下载脚本读取索引中已有的 URL，获取服务器提供的模型 ZIP；它不会把 GeoJSON 转换成三维模型。

## 1. 五套数据概览

下表数量来自本地索引，代表分块/图幅数，不代表建筑物数量。

| 目录 | 数据含义 | 唯一分块数 | 索引提供的模型格式 | 下载工具 |
|---|---|---:|---|---|
| [3D Photo-realistic Model](./3D%20Photo-realistic%20Model/) | 规划署三维实景模型，覆盖部分香港岛和九龙半岛 | 2,150 | OBJ、OSGB、Cesium 3D Tiles | 全量下载脚本、中环相邻分块测试脚本 |
| [3D Spatial Data 3D-BIT00](./3D%20Spatial%20Data%203D-BIT00/) | 地政总署三维空间数据，表达建筑物、基础设施、地形等的形状、外观和位置 | 3,295 | 3DS、FBX、MAX、VRML | 通用下载脚本、相邻图幅测试脚本 |
| [Individualised models](./Individualised%20models/) | 可视化三维地图的单体化模型，包含几何与纹理影像，按地物组织 | 3,456 | FBX、glTF、MAX | 暂无专用下载脚本 |
| [Non-textured models](./Non-textured%20models/) | 可视化三维地图的无纹理模型，包含建筑物、基础设施、地形等几何数据 | 3,456 | FBX、glTF、MAX | 暂无专用下载脚本 |
| [Tile-based models](./Tile-based%20models/) | 可视化三维地图的方格形式模型，基于倾斜航拍图像制作的网格模型 | 3,455 | OBJ、OSGB、3D Tiles | 暂无专用下载脚本 |

后三类是地政总署可视化三维地图的不同产品。“单体化”描述模型内部的对象组织方式；该产品仍然按图幅提供下载，一个 ZIP 不等于一栋建筑。

产品定义参考[地政总署三维制图说明](https://www.landsd.gov.hk/tc/survey-mapping/mapping/3d-mapping.html)及[规划署三维实景模型说明](https://data.gov.hk/sc-data/dataset/hk-pland-pland1-3d-photo-realistic-model)。规划署产品与地政总署 Tile-based 产品虽然都提供实景模型和部分相同格式，但属于不同数据产品。

## 2. 目录结构

以下为简化结构；各产品保存的索引格式并不完全相同。

```text
3D Visualisation Map/
├─ README.md
├─ .gitignore
├─ 3D Photo-realistic Model/
│  ├─ OpenData_3D_HK80_OpenData_3D_HK80_converted.geojson
│  ├─ full_download_models.py
│  ├─ download_central_obj_test.py
│  ├─ DATA_PROFILING.md
│  ├─ 3D_Photo_realistic_Model_{GEOJSON,GEOPACKAGE,GML,KML,SHP,FGDB}/
│  └─ skills/dataset-download-profiler/SKILL.md
├─ 3D Spatial Data 3D-BIT00/
│  ├─ b1000_Tile_Apr2026_gdb_b1000_Tile_converted.geojson
│  ├─ download_3d_bit00.py
│  ├─ download_test_adjacent_tiles.py
│  ├─ data_profiling.md
│  ├─ 3D_Spatial_Data_3D_BIT00_{GEOJSON,GEOPACKAGE,GML,KML,FGDB}/
│  └─ skills/dataset-download-profiler/SKILL.md
├─ Individualised models/
│  ├─ 3DVM_F1_20260908_Individualised_models_converted.geojson
│  └─ Individualised_models_{GEOPACKAGE,GML,FGDB}/
├─ Non-textured models/
│  └─ Non_textured_models_{GEOJSON,GEOPACKAGE,GML,KML,SHP,FGDB}/
└─ Tile-based models/
   ├─ F2_3DVisualisationMapTilebasedModels_20260908_Tile_based_models_converted.geojson
   └─ Tile_based_models_{GEOPACKAGE,GML,FGDB}/
```

`{...}` 表示多个实际目录，不是一个目录的名称。`DATA_PROFILING.md` / `data_profiling.md` 是已有的子项目分析文档；`skills/.../SKILL.md` 是分析工作流说明，均不属于模型数据。

## 3. 为什么不同目录中有相同或相似的文件？

### 3.1 同一套索引可以保存为多种格式

本项目的 GeoJSON 主要是模型分块索引；其他 GIS 格式也主要保存同一套分块信息。GeoJSON 本身并非只能用于索引，这里是由具体内容决定其用途。

| 格式或文件 | 在项目中的作用 |
|---|---|
| `.geojson` | 以 JSON 保存分块边界和属性，便于脚本读取 |
| `.gpkg`（GeoPackage） | 用一个数据库文件保存空间数据 |
| `.gml` + `.xsd` | GML 保存数据，XSD 定义字段和结构 |
| `.kml` | 保存供 KML 软件读取的空间要素 |
| `.shp` + `.dbf` + `.shx` + `.prj` 等 | 共同组成 Shapefile；分别承担几何、属性、记录索引、坐标系等职责 |
| `.gdb` 目录（FGDB） | File Geodatabase；内部包含数据表、系统信息和数据库索引 |

本次交叉核对结果：

- 五套数据各自的 GeoJSON 与 GPKG，分块编号集合和模型下载 URL 完全一致。
- 各自的 GML，分块数量与编号集合和 GeoJSON 一致。
- 已有 KML 的要素数、SHP 配套 DBF 的记录数，与对应 GeoJSON 一致。

因此，一个下载流程通常选择一种索引作为输入即可。上述核对不代表所有格式的每个字段、坐标数字或文件字节都完全相同。

格式转换可能改变字段名和坐标表达。例如无纹理模型的 DBF 中，`Format_glTF` 变成了 `Format_glT`，`REVISIONDATE` 变成了 `REVISIONDA`。部分 GPKG 使用香港网格坐标 `EPSG:2326`，另一些使用经纬度 `EPSG:4326`；使用空间边界前需要检查坐标系。

有的目录没有 KML/SHP，仅凭本地文件无法确定是未下载还是来源未提供。

### 3.2 FGDB 的同名文件属于数据库内部结构

不同 `.gdb` 中都可能出现 `a00000001.gdbtable`、`.gdbtablx`、`.gdbindexes`、`.atx` 等文件。名称中的编号是数据库内部编号，不是模型或地图产品编号。

哈希比较确认，部分跨产品的同名内部文件连内容也完全相同；这与共享数据库系统结构相符，不能据此判断整套地图重复。应把整个 `.gdb` 作为一个数据库管理，不能仅凭同名删除其内部文件。

### 3.3 不同产品可以使用相同图幅

本地 Individualised 与 Non-textured 索引的 3,456 个图幅编号完全一致，GeoJSON 中的边界几何也逐个完全一致，但模型下载 URL 不同：

```text
单体化 FBX：/api/3d-zip/FBX/1-SE-19D.zip
无纹理 FBX：/api/3d-zip/FBX0/1-SE-19D.zip
```

相同编号表示同一个地理范围，路径中的 `FBX` 与 `FBX0` 区分产品。相同边界不能证明模型几何、对象数量或属性完全相同。

Tile-based 的本地图幅集合比前两者少 `2-SE-1D`，共 3,455 幅。

### 3.4 项目内存在两组完全相同的 GeoJSON 副本

Photo-realistic 和 3D-BIT00 两个目录，都在项目根层和各自 `*_GEOJSON` 子目录保存了一份索引。每个项目内部的两份 GeoJSON 经 SHA-256 比较，字节完全相同。

现有脚本默认读取各自项目根层的那份文件。该布局方便脚本找到输入文件，但不能从现有文件确定具体复制历史。

## 4. 下载 URL 从哪里来？

### 4.1 下载链路

```text
本地空间索引
  → 选定图幅/分块
  → 读取 properties 中所选格式的 URL
  → HTTP GET 请求官方服务器
  → 将响应保存为 ZIP
  → 后续解压、导入三维软件或进行格式转换
```

当前脚本使用索引中已经存在的完整 URL；不需要根据坐标猜测地址，也没有将索引转换成模型。全量下载脚本和两个 3D-BIT00 脚本不执行解压；中环测试脚本会校验并解压 ZIP。它们均不执行模型格式转换。

### 4.2 字段与下载服务对应关系

| 产品 | 图幅字段 | 模型 URL 字段 | 下载域名及路径类别 |
|---|---|---|---|
| Photo-realistic | `GRID_NAME` | `OBJ_URL`、`OSGB_URL`、`Cesium_URL` | `pdmap.pland.gov.hk/PLANDWEB/public/3d_photo_realistic_models/` 下的 `obj`、`osgb`、`Cesium` |
| 3D-BIT00 | `SHEETNO` | `Format_3DS`、`Format_FBX`、`Format_MAX`、`Format_VRML` | `download.map.gov.hk/api/3d-zip/` 下的 `3DS3DBIT00`、`FBX3DBIT00`、`MAX3DBIT00`、`VRML3DBIT00` |
| Individualised | `SHEETNO` | `Format_FBX`、`Format_glTF`、`Format_MAX` | 同一地政总署服务下的 `FBX`、`GLTF`、`MAX` |
| Non-textured | `SHEETNO` | `Format_FBX`、`Format_glTF`、`Format_MAX` | 同一地政总署服务下的 `FBX0`、`GLTF0`、`MAX0` |
| Tile-based | `SHEETNO` | `Format_OBJ`、`Format_OSGB`、`Format_3D_Tiles` | 同一地政总署服务下的 `OBJ`、`OSGB`、`CESIUM` |

本地实景模型索引中的完整 URL 示例：

```text
https://pdmap.pland.gov.hk/PLANDWEB/public/3d_photo_realistic_models/obj/Tile_+005_+006_OBJ.zip
```

3D-BIT00 地址结构示例，省略了查询参数值，不能直接复制用于下载：

```text
https://download.map.gov.hk/api/3d-zip/FBX3DBIT00/3D-BIT00_13SE11B_FBX.zip?key=…
```

`key` 参数已包含在本地索引中，现有脚本直接使用完整 URL，不自行生成该参数。URL 路径和图幅编号的大小写应以索引原值为准。

后三类产品还包含以下字段：

- `URL_3D_Visualisation_Map`：地图网站入口。
- `Download_API`：下载接口说明或入口页面。
- `Format_*`：具体图幅、具体格式的实际模型下载链接。

最初获取这些索引时使用的网页按钮、导出步骤或历史命令，当前没有充分记录可还原。本 README 说明的是现有文件内容与代码行为，不代表逐条链接已经重新联网验证可用。

## 5. 怎样判断两个编号区块相邻？

**依据是空间索引中的边界坐标与多边形，而不是编号连续或文件排列顺序。** 本节的“相邻”指共用一段长度大于零的边界；仅角点接触不算共边相邻。

### 5.1 `13-SE-11B` 与 `13-SE-12A` 的实际证据

在 [3D-BIT00 GeoJSON 索引](./3D%20Spatial%20Data%203D-BIT00/b1000_Tile_Apr2026_gdb_b1000_Tile_converted.geojson) 中，按 `properties.SHEETNO` 查找这两条记录，其属性为：

| 图幅编号 | `Min_x` | `Max_x` | `Min_y` | `Max_y` |
|---|---:|---:|---:|---:|
| `13-SE-11B` | 808250 | 809000 | 803000 | 803600 |
| `13-SE-12A` | 809000 | 809750 | 803000 | 803600 |

这些属性是香港 1980 网格坐标，单位为米；同套 GeoPackage 的 `gpkg_geometry_columns.srs_id` 为 `2326`（EPSG:2326）。X 为东向坐标，Y 为北向坐标。

- 第一幅的 `Max_x` 等于第二幅的 `Min_x`，都是 `809000`。
- 两幅的 Y 区间完全相同，都是 `[803000, 803600]`。
- 因此 `13-SE-11B` 在西、`13-SE-12A` 在东，共用从 `(809000, 803000)` 到 `(809000, 803600)` 的完整边界，长度为 **600 米**。

同时核对 GeoJSON 的 `geometry.coordinates`：两幅多边形都包含以下线段，端点坐标完全一致，只是遍历方向相反：

```text
(113.9125019877, 22.1652669272)
                 ↕
(113.9124918609, 22.1706853259)
```

这里的几何坐标是经度、纬度，与上表属性中的米制网格坐标采用不同表达，不能直接混用。边界属性和实际多边形共同支持这两幅东西相邻的结论，不需要读取下载后的模型。

### 5.2 如何复核其他区块

先确认同一产品、同一坐标系，再按编号取出索引记录。对于轴对齐矩形区块 A、B：

- **东西共边**：`A.Max_x = B.Min_x`（或反过来），且 `min(A.Max_y, B.Max_y) > max(A.Min_y, B.Min_y)`。
- **南北共边**：`A.Max_y = B.Min_y`（或反过来），且 `min(A.Max_x, B.Max_x) > max(A.Min_x, B.Min_x)`。

上述严格大于号要求重叠区间有正长度，排除了仅角点接触。若区块不是轴对齐矩形，包围盒只能用于初筛，还要检查实际多边形内部不重叠、边界交集有正长度；涉及坐标转换或浮点误差时，应按坐标单位和数据精度设置容差。

[`download_test_adjacent_tiles.py`](./3D%20Spatial%20Data%203D-BIT00/download_test_adjacent_tiles.py) 的 `TARGET_SHEETS` 只是固定列出这两个编号，代码只按编号查 URL，**没有自动检验相邻关系**。本节结论来自对本地索引的坐标核对，不能仅以脚本名称作为证据。

实景模型的中环测试脚本 [`download_central_obj_test.py`](./3D%20Photo-realistic%20Model/download_central_obj_test.py) 则在 `select_tiles()` 中检查 `MIN_X`、`MAX_X`、`MIN_Y`、`MAX_Y`，要求各块 X 范围一致、南块 `MAX_Y` 等于北块 `MIN_Y`，以验证选定的矩形分块南北共边。两个产品的字段大小写不同，读取时需使用各自索引的原字段名。

## 6. 下载脚本与使用方法

运行环境：**Python 3.10 或以上**。下载脚本均使用 Python 标准库，不需要额外安装 Python 包。执行实际下载需要能够访问对应官方服务器。

下面每个子项目的第一条 `Set-Location` 命令均假设当前位于仓库根目录。

### 6.1 Photo-realistic 下载脚本

脚本：[full_download_models.py](./3D%20Photo-realistic%20Model/full_download_models.py)

默认读取同目录的 GeoJSON；默认下载全部图幅的 OBJ，使用 3 个并发任务、最多 3 次尝试，默认执行 ZIP 完整性校验。

```powershell
Set-Location '.\3D Photo-realistic Model'

# 预览某一图幅的三种格式；指定输出目录以固定任务位置
python full_download_models.py --tile 'Tile_+005_+006' --format all --output '.\download' --dry-run

# 下载某一图幅的 OBJ
python full_download_models.py --tile 'Tile_+005_+006' --format obj --output '.\download'

# 下载该图幅的全部三种格式
python full_download_models.py --tile 'Tile_+005_+006' --format all --output '.\download'

# 对原下载目录补齐全索引 OBJ；先确认没有任务同时写入此目录
python full_download_models.py --format obj --output '.\download' --workers 3
```

需要了解的代码行为：

- `--format` 支持小写 `obj`、`osgb`、`cesium`、`all`；`--tile` 可以重复指定。
- 不传 `--output` 时，如果默认 `download` 非空，脚本会另建带时间戳的目录。继续已有下载时应明确指定原目录。
- `--dry-run` 不发送下载请求，但会先创建或选择输出目录。
- 默认检查已有非空 ZIP，校验通过后跳过；发现无效的已有 ZIP 会标记 `invalid_existing`，不会自动覆盖修复。
- 下载先写 `.zip.part`，请求结束后改名为 `.zip`，再执行校验。`--no-validate` 可关闭校验。
- 全部任务结束后写入 `download_report.csv`；缺少报告本身不说明下载已经失败或停止。
- `.part` 每次重试按 `wb` 从头写入，未实现 HTTP `Range` 字节级断点续传。

### 6.2 3D-BIT00 通用下载脚本

脚本：[download_3d_bit00.py](./3D%20Spatial%20Data%203D-BIT00/download_3d_bit00.py)

默认下载 FBX，可按图幅、格式和任务数量筛选；按顺序执行下载。

```powershell
Set-Location '.\3D Spatial Data 3D-BIT00'

# 仅预览一个图幅的 FBX 下载任务
python download_3d_bit00.py --format FBX --sheetno '13-SE-11B' --dry-run

# 实际下载该图幅的 FBX
python download_3d_bit00.py --format FBX --sheetno '13-SE-11B' --skip-existing

# 下载该图幅的全部四种格式；ALL 必须使用大写
python download_3d_bit00.py --format ALL --sheetno '13-SE-11B' --skip-existing
```

- 默认 GeoJSON 路径相对于当前工作目录，因此示例先进入脚本所在目录。
- 相对 `--out-dir` 路径以脚本所在目录为基准，默认是 `download`。
- `--limit` 限制的是下载文件/任务数，选择多格式时不等于图幅数。
- `--skip-existing` 仅检查目标路径是否存在，不验证文件完整性；未传该参数时会覆盖同路径文件。
- 直接写入 ZIP，没有 `.part` 机制、ZIP 完整性校验、自动重试或字节级断点续传。中断后即使文件名为 `.zip`，内容也可能不完整。

### 6.3 3D-BIT00 相邻图幅测试脚本

脚本：[download_test_adjacent_tiles.py](./3D%20Spatial%20Data%203D-BIT00/download_test_adjacent_tiles.py)

固定读取 `13-SE-11B`、`13-SE-12A` 两幅的 `Format_FBX`，输出到脚本旁的 `download`，文件名为 `<图幅>_FBX.zip`。该脚本会覆盖同路径 ZIP，仅检查结果非空，不执行解压或 ZIP 完整性校验。

### 6.4 能否一个脚本下载五套地图？

**现有脚本针对各自地图产品，支持该产品的多种格式，并不是五套产品通用下载器。**

例如实景模型脚本根据 `GRID_NAME` 和 `OBJ_URL` 等字段工作；3D-BIT00 脚本根据 `SHEETNO` 和 `Format_*` 工作，并限定了可选格式。

后三类地图虽然也提供完整下载 URL，但当前没有专门下载脚本。要复用现有代码，需要适配索引路径、图幅字段、格式映射、文件命名和校验规则；仅替换 GeoJSON 文件名不保证能够正确运行。

## 7. 资料入口

- [地政总署：三维制图及各产品说明](https://www.landsd.gov.hk/tc/survey-mapping/mapping/3d-mapping.html)
- [DATA.GOV.HK：三维空间数据 3D-BIT00](https://data.gov.hk/sc-data/dataset/hk-landsd-openmap-development-hkms-digital-3d-bit00)
- [Open3Dhk 下载接口入口](https://3d.map.gov.hk/download-api)
- [DATA.GOV.HK：规划署三维实景模型](https://data.gov.hk/sc-data/dataset/hk-pland-pland1-3d-photo-realistic-model)
- [CSDI：规划署三维实景模型数据集](https://portal.csdi.gov.hk/csdi-webpage/dataset/pland_rcd_1636534828693_9849)

**判断两个文件是否代表同一套模型，需要同时看产品、图幅、下载 URL 和实际内容；相同扩展名或相同图幅编号都不足以证明模型重复。**
