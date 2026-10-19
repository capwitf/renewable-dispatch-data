# 公开新能源调度数据 | Open Renewable Energy Dispatch Data

[简体中文](#简体中文) | [English](#english)

可复现的风电、光伏调度数据来源、核验报告、示例时序与读取工具。数据集、统计口径和许可边界分别说明，避免把资源数据、实际出力与预测值混为一谈。

Reproducible sources, validation reports, sample time series, and readers for wind and solar dispatch research. Dataset provenance, statistical definitions, and license boundaries are documented separately.

## 简体中文

### 内容

| 目录 | 内容 | 适用方向 | 重要限制 |
|---|---|---|---|
| `01_电氢氨园区协同优化调度_公开数据/` | 风光数据核验报告与目录、EIA ERCOT 2025 示例 CSV、下载/整理脚本、OPSD 数据包元数据 | 历史出力参考、资源建模、调度数据源筛选 | EIA 示例是 ERCOT 系统级实际净发电，不是园区/电站数据，也不含风光预测；2025 UTC 年序列有 24 小时官方数据缺失，未插补 |
| `02_新能源不确定性优化调度_严格配对数据/` | 严格筛选报告、合格数据摘要、官方获取清单、PERFORM HDF5 转 CSV 工具 | 预测误差、概率场景、机会约束、随机与鲁棒调度 | SMARD、ENTSO-E、PERFORM 原始数据按报告所述从官方渠道取得；PERFORM `actuals` 是模型化基准，不是电表实测 |

### 快速开始

运行 EIA 示例数据下载脚本（需要 Python 3.10+ 与 `requests`）：

```powershell
python -m pip install requests
python "01_电氢氨园区协同优化调度_公开数据/download_eia930_ercot_2025.py" --output-dir data/eia
python "01_电氢氨园区协同优化调度_公开数据/densify_eia_2025.py" --input data/eia/EIA930_ERCO_Wind_Solar_2025_hourly.csv --output data/eia/EIA930_ERCO_Wind_Solar_2025_8760_UTC_missing_explicit.csv
```

PERFORM HDF5 转 CSV 工具的依赖与示例：

```powershell
python -m pip install -r "02_新能源不确定性优化调度_严格配对数据/读取工具/requirements.txt"
python "02_新能源不确定性优化调度_严格配对数据/读取工具/read_perform_h5_to_csv.py" actual --input BA_wind_actuals_2018.h5 --output wind_actual.csv
python "02_新能源不确定性优化调度_严格配对数据/读取工具/read_perform_h5_to_csv.py" forecast --input BA_wind_day-ahead_fcst_2018.h5 --output wind_forecast.csv --percentile 50
```

### 数据边界

- `EIA930_ERCO_Wind_Solar_2025_8760_UTC_missing_explicit.csv` 保留完整 8,760 小时 UTC 索引；缺失的 24 小时留空并标明状态，没有插值或补值。
- EIA 的风光值是 ERCOT 平衡区按燃料类型汇总的实际净发电量，不能用于构造风光预测误差，也不能直接代表某一园区。
- 第二套报告将实际—预测配对来源限定为 SMARD、ENTSO-E 和 NREL/OEDI PERFORM；下载数据前应重新核实数据项的最新许可、时区、筛选条件与引用方式。
- 报告中的许可说明是核验时的记录，不替代数据发布方的当前条款。上游数据需按其发布方许可使用并保留来源与引用信息。

### 许可

- 本仓库自编脚本：MIT，见 [LICENSE](LICENSE)。
- 本仓库原创报告、目录与说明：CC BY 4.0，见 [LICENSE-DOCUMENTATION](LICENSE-DOCUMENTATION)。
- 随仓库分发的第三方数据、元数据和标识不由上述许可重新授权；请遵循 [第三方来源与许可说明](THIRD_PARTY_NOTICES.md) 及各发布方现行条款。

## English

### What's Included

| Directory | Contents | Intended use | Important limitation |
|---|---|---|---|
| `01_电氢氨园区协同优化调度_公开数据/` | Validation report and catalog, EIA ERCOT 2025 sample CSVs, download/processing scripts, and OPSD package metadata | Historical generation references, resource modeling, and data-source selection | The EIA sample is ERCOT system-level actual net generation, not plant/site data, and has no wind/solar forecasts. Its 2025 UTC series has 24 hours missing in the official response; no imputation was applied. |
| `02_新能源不确定性优化调度_严格配对数据/` | Screening report, qualified dataset summary, official source list, and a PERFORM HDF5-to-CSV reader | Forecast errors, probabilistic scenarios, chance constraints, stochastic and robust dispatch | Obtain SMARD, ENTSO-E, and PERFORM source data from the official channels described in the report. PERFORM `actuals` are modelled benchmarks, not meter readings. |

### Quick Start

Download the EIA sample (Python 3.10+ and `requests` required):

```powershell
python -m pip install requests
python "01_电氢氨园区协同优化调度_公开数据/download_eia930_ercot_2025.py" --output-dir data/eia
python "01_电氢氨园区协同优化调度_公开数据/densify_eia_2025.py" --input data/eia/EIA930_ERCO_Wind_Solar_2025_hourly.csv --output data/eia/EIA930_ERCO_Wind_Solar_2025_8760_UTC_missing_explicit.csv
```

Install the PERFORM reader dependencies and export an HDF5 file:

```powershell
python -m pip install -r "02_新能源不确定性优化调度_严格配对数据/读取工具/requirements.txt"
python "02_新能源不确定性优化调度_严格配对数据/读取工具/read_perform_h5_to_csv.py" actual --input BA_wind_actuals_2018.h5 --output wind_actual.csv
python "02_新能源不确定性优化调度_严格配对数据/读取工具/read_perform_h5_to_csv.py" forecast --input BA_wind_day-ahead_fcst_2018.h5 --output wind_forecast.csv --percentile 50
```

### Data Boundaries

- `EIA930_ERCO_Wind_Solar_2025_8760_UTC_missing_explicit.csv` preserves the full 8,760-hour UTC index. The 24 missing hours remain blank and are flagged; no interpolation or imputation was applied.
- EIA values are ERCOT balancing-area actual net generation aggregated by fuel type. They cannot be used to derive wind/solar forecast errors or treated as plant-level output.
- The second report screens actual/forecast paired sources from SMARD, ENTSO-E, and NREL/OEDI PERFORM. Recheck current terms, time zones, query filters, and citation requirements before downloading data.
- License notes in the reports record the state of verification at review time and do not replace the providers' current terms. Use upstream data under the applicable provider terms and retain provenance and citations.

### Licenses

- Original scripts in this repository: MIT, see [LICENSE](LICENSE).
- Original reports, catalogs, and documentation: CC BY 4.0, see [LICENSE-DOCUMENTATION](LICENSE-DOCUMENTATION).
- Third-party data, metadata, and marks distributed with this repository are not relicensed by those files. See [third-party notices](THIRD_PARTY_NOTICES.md) and the providers' current terms.
