# StaMPS_octave_python — 工作進度記錄
> 最後更新：2026-05-26
> 供下次開啟 Claude Code 時快速銜接上下文。

---

## 專案位置

| 項目 | 路徑 |
|------|------|
| 本地目錄 | `~/tools/StaMPS_octave_python/` |
| GitHub   | https://github.com/choin0207/StaMPS_octave_python |
| 原始 StaMPS | `~/StaMPS-4.1-beta/` |

---

## 專案目標

將 StaMPS-4.1-beta（原為 MATLAB）改寫為：
1. **Octave 相容版**：修補 MATLAB 專屬語法，使 `stamps(1,8)` 可在 GNU Octave 執行
2. **Python 畫圖層**：以 `ps_plot.py`（matplotlib）取代 `ps_plot.m`（MATLAB GUI）
3. 開源發布於 GitHub，包含完整說明文件

---

## Git Commit 歷史（最新在上）

```
cfe3f04  docs: README 新增 export_ps 說明與 ps_plot.py 完整用法參考
904c955  feat: ps_plot.py 加入完整用法註記與 export_ps() 匯出功能
c275163  docs: 補充完整安裝、環境設定、執行與畫圖說明
eefeb38  feat: 修改 bin/ 腳本，將 matlab 替換為 octave
204393e  feat: 新增 Octave 相容版 .m 檔案（125 個）
7d6ce03  feat: 初始化 StaMPS Octave+Python 移植專案
```

---

## 已完成工作

### 1. Octave 相容性修補

| 檔案 | 問題 | 修法 |
|------|------|------|
| `matlab/azi_f_resample.m` | `fdesign.rsrc()` + `design()` + `upfirdn()` 為 MATLAB Signal Toolbox 專屬 | 改用 Octave `resample(patch_tmp, L, M)` |
| `matlab/batchjob.m` | `textread()` 已棄用 | 改用 `textscan()` + `fopen/fclose` |
| `matlab/ps_select.m` | `parfor` 需 Parallel Computing Toolbox | 加 `pkg load parallel` 守衛（Octave） |
| `matlab/ps_est_gamma_quick.m` | 同上 | 同上 |
| `matlab/ps_scn_filt.m` | 同上 | 同上 |
| `matlab/ps_scn_filt_krig.m` | 同上 | 同上 |

### 2. bin/ 腳本修補

- 共 128 個 shell 腳本，14 個含 `matlab -` 呼叫
- 全部替換為 `octave --no-gui --quiet`
- 驗證：`grep -r 'matlab -' bin/` 回傳 0 筆

### 3. Python 畫圖層（`python/ps_plot.py`，~700 行）

- `load_mat(path)`：支援 v5 + v7.3 HDF5
- `load_cpt(cpt_path)`：GMT CPT → matplotlib colormap
- `PSPlot` 類別：
  - `getparm(key, default)` ← 對應 MATLAB `getparm()`
  - `_load_ps_data()` ← 讀取 `ps<ver>.mat`
  - `_get_ph_all(value_type)` ← 回傳 (ph_all, units, fig_name, is_complex)
  - `plot(...)` ← 速度/高程/干涉圖/時間序列
  - `export_ps(value_type, out_path, fmt, lon_rg, lat_rg, no_header)` ← CSV/TXT 輸出
- 完整 docstring（對應 ps_plot.m 格式）：28 種 value_type、CLI 用法、Python API 範例
- CLI 新增 `--export`、`--fmt`、`--no-header` 參數

### 4. export_ps() 輸出格式

```
# CSV（預設）
lon,lat,v_d_mmPyr
121.043210,24.123456,-3.2150

# TXT（空格分隔）
lon lat v_d_mmPyr
121.043210 24.123456 -3.2150
```

- 欄位名規則：`value_type.replace("-","_") + "_" + units.replace("/","p")`
- 2-D phase 類型（如 `w`、`u6`）拒絕輸出，拋出 `ValueError("1-D ...")`

### 5. 測試（`tests/test_ps_plot.py`，10 個測試，全部通過）

| 測試名稱 | 驗證內容 |
|---------|---------|
| test_import | PSPlot、load_mat、load_cpt 可匯入 |
| test_load_cpt | GMT_jet.cpt → LinearSegmentedColormap |
| test_psplot_init | work_dir 正確設定 |
| test_getparm_default | 無 parms.mat 時回傳 default |
| test_load_mat_v5 | scipy savemat → load_mat 形狀正確 |
| test_invalid_value_type | 非法 value_type 拋出 ValueError |
| test_export_ps_csv | CSV 格式、行數、header、3 欄 |
| test_export_ps_txt | 空格分隔、無逗號 |
| test_export_ps_spatial_filter | lon/lat 過濾減少點數 |
| test_export_ps_rejects_phase | w 類型拋出 ValueError("1-D") |

執行命令：
```bash
cd ~/tools/StaMPS_octave_python
python3 -m pytest tests/test_ps_plot.py -v
```

### 6. 說明文件（`README.md`，648 行，9 節）

| 節 | 內容 |
|----|------|
| §1 | 系統需求（Octave 8+、Python 3.8+、必要套件） |
| §2 | 安裝（setup.sh 一鍵 + 手動步驟） |
| §3 | 環境設定與 4 個驗證指令 |
| §4 | 執行 StaMPS（mt_prep_gamma → stamps(1,8) → ps_merge_patches） |
| §5 | 畫圖（ps_plot.py 所有用法） |
| §6 | 匯出 PS 資料（CLI + Python API + GMT 整合） |
| §7 | ps_plot.py 完整用法參考（所有 value_type、MATLAB↔Python API 對照） |
| §8 | Octave 相容性修補表 |
| §9 | 目錄結構 |

---

## 環境設定

```bash
# 載入環境（每次開新 terminal 需執行）
source ~/tools/StaMPS_octave_python/StaMPS_CONFIG.bash

# 或永久加入 ~/.bashrc
echo 'source ~/tools/StaMPS_octave_python/StaMPS_CONFIG.bash' >> ~/.bashrc
```

`StaMPS_CONFIG.bash` 設定：
```bash
export STAMPS=~/tools/StaMPS_octave_python
export PATH=$STAMPS/bin:$PATH
export OCTAVE_PATH=$STAMPS/matlab:${OCTAVE_PATH:-}
export PYTHONPATH=$STAMPS/python:${PYTHONPATH:-}
export LC_NUMERIC=en_US.UTF-8
```

---

## 尚未驗證的部分（未來工作）

1. **實際執行 stamps(1,8)**：目前修補僅基於靜態分析，尚未用真實資料跑完整流程
2. **Octave parallel 套件**：`pkg load parallel` 需先安裝 `octave-parallel`
3. **APS 校正 value_type**：`v-a`、`v-da`、`v-dao` 在 ps_plot.py 尚未實作
4. **TRAIN toolbox 整合**：ps_plot.py 目前不支援 TRAIN-corrected results
5. **ps_plot.py Step 2–4 替代**：目前只替代畫圖（Step 7–8），Step 2–4 仍需 Octave

---

## 快速指令參考

```bash
# 進入專案
cd ~/tools/StaMPS_octave_python

# 跑測試
python3 -m pytest tests/test_ps_plot.py -v

# 畫速度圖
python3 python/ps_plot.py --work-dir /path/to/stamps/output --value-type v-d

# 匯出 CSV
python3 python/ps_plot.py --work-dir /path/to/stamps/output --value-type v-d \
    --export output.csv --fmt csv

# Python API
from python.ps_plot import PSPlot
p = PSPlot(work_dir='/path/to/stamps/output')
p.plot('v-d', bg=1)
p.export_ps('v-d', 'ps_velocity.csv', fmt='csv')

# 推送 GitHub
cd ~/tools/StaMPS_octave_python
git add -A && git commit -m "feat: ..." && git push
```

---

## 關鍵檔案路徑

```
~/tools/StaMPS_octave_python/
├── RESUME.md                    ← 本檔案
├── README.md                    ← 完整說明文件（648 行）
├── StaMPS_CONFIG.bash           ← 環境變數設定
├── setup.sh                     ← 一鍵安裝腳本
├── python/
│   ├── ps_plot.py               ← 主要 Python 畫圖程式（~700 行）
│   └── __init__.py
├── matlab/                      ← Octave 相容版 .m 檔案（125 個）
│   ├── azi_f_resample.m         ← 已修補（Signal Toolbox）
│   ├── batchjob.m               ← 已修補（textread）
│   ├── ps_select.m              ← 已修補（parfor）
│   ├── ps_est_gamma_quick.m     ← 已修補（parfor）
│   ├── ps_scn_filt.m            ← 已修補（parfor）
│   ├── ps_scn_filt_krig.m       ← 已修補（parfor）
│   └── cptfiles/GMT_jet.cpt
├── bin/                         ← Shell 腳本（128 個，14 個已修補）
├── tests/
│   └── test_ps_plot.py          ← 10 個測試，全部通過
└── docs/
    └── octave_compat.md         ← 相容性修補詳細說明
```
