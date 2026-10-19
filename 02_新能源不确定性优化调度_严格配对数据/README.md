# 新能源不确定性优化调度数据包

本压缩包汇集了针对“风电/光伏实际—预测配对时序”严格筛选后的**官方数据获取信息、引用信息和读取工具**。它不混入 EIA-930、仅实际值、仅资源数据或未经核验为完整年度实际—预测配对的 ERCOT 原生报告。

> **使用前须知。** 压缩包本身不复制 SMARD 或 ENTSO-E 的大规模原始数据，因为应由研究者按所选区域、年份、粒度和许可条款从官方入口重新下载并保存查询条件。PERFORM 的公开 HDF5 体量较大，压缩包提供已核验的官方对象链接和读取脚本。这样可避免将不同区域、时间尺度或许可版本的文件误当作同一个数据集。

## 包内文件

| 位置 | 内容 | 用途 |
|---|---|---|
| `报告与目录/严格筛选核验报告.md` | 完整核验报告 | 阅读来源、字段、时区、预测提前期、格式、许可和引用。 |
| `报告与目录/合格数据集摘要.csv` | 机器可读摘要 | 快速筛选候选数据集。 |
| `官方获取清单/官方链接与对象清单.csv` | 官方入口、已验证 PERFORM 对象链接与下载说明 | 以官方链接取得原始文件。 |
| `读取工具/read_perform_h5_to_csv.py` | PERFORM HDF5 读取/导出模板 | 将实际、日前预测、日内预测或小时内预测文件输出为 tidy CSV。 |
| `读取工具/requirements.txt` | Python 包依赖 | 安装读取工具依赖。 |

## 推荐使用路径

若研究重点是概率预测误差、场景生成、机会约束或两阶段随机优化，优先使用 **NREL ARPA-E PERFORM**。其 HDF5 实际文件含 `actuals` 和 `time_index`，预测文件含 `forecasts`、`issue_time`、`forecast_time`；日前预测提供 1–99 百分位，适合直接构造概率场景。请特别注意，PERFORM 的 `actuals` 是 NREL 基于 NSRDB/SAM（光伏）与 WRF（风电）生成的模型化基准，不是电站电表计量值。

如果研究希望使用官方市场/透明度平台的实现发电和业务预测，优先使用 **SMARD**。在官方数据下载中心针对同一地区和年度分别导出 `Actual generation`、`Forecasted generation Day-Ahead` 与可选的 `Generation Forecast Intraday`；能源类别选择 `Wind Onshore`、`Wind Offshore`、`Photovoltaik`；格式选择 CSV；15 分钟或小时均可。SMARD 时间为 CET/CEST，合并前必须妥善处理夏令时。

如果需要多国/跨竞价区比较，使用 **ENTSO-E Transparency Platform**。将 `Actual Generation per Production Type [16.1.B&C]` 与 `Generation Forecasts for Wind and Solar [14.1.D]` 以相同区域和交付期间导出，再用 UTC 时间戳配对。平台提供网页导出、REST API 和 File Library 的 CSV extracts；REST API 可能需要注册 security token。

## 论文引用

PERFORM 的官方数据集引用为：

> Sergi, B., Feng, C., Zhang, F., Hodge, B., Ring-Jarvi, R., Bryce, R., Doubleday, K., Rose, M., Buster, G., & Rossol, M. (2022). *ARPA-E PERFORM datasets* [Data set]. Open Energy Data Initiative (OEDI). National Renewable Energy Laboratory (NREL). https://doi.org/10.25984/1891136

SMARD 建议在论文中注明 Bundesnetzagentur、具体产品名、地区、分辨率、下载日期和下载中心链接。ENTSO-E 建议注明数据项编号、区域、期间、访问日期以及所用文件库提取或 API 查询参数。详细格式见主报告。

## 不纳入的数据

EIA Form EIA-930 只含按燃料类型的实际净发电，不能构造风光预测误差；ERCOT NP4-733/NP4-738 是实际值与潜力而非实际—预测配对；因此均未纳入本包的合格主清单。

