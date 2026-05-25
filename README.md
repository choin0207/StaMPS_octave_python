# StaMPS Octave + Python Edition

**StaMPS 4.1-beta** 的開源移植版本，以 **GNU Octave** 取代 MATLAB（計算核心），以 **Python / matplotlib** 取代 `ps_plot.m`（視覺化），完全免費、零授權費用。

| 原始 StaMPS | 本版本 |
|---|---|
| MATLAB（商業授權）| GNU Octave 8.x（GPL 免費）|
| MATLAB Parallel Computing Toolbox | `octave-parallel` 套件 |
| MATLAB Signal Processing Toolbox | `octave-signal` 套件 |
| `ps_plot.m`（MATLAB 繪圖）| `python/ps_plot.py`（matplotlib GUI）|

---

## 目錄

1. [系統需求](#1-系統需求)
2. [安裝](#2-安裝)
3. [設定環境變數](#3-設定環境變數)
4. [執行 StaMPS](#4-執行-stamps)
5. [畫圖（ps_plot.py）](#5-畫圖ps_plotpy)
6. [匯出 PS 點資料（export_ps）](#6-匯出-ps-點資料export_ps)
7. [ps_plot.py 完整用法參考](#7-ps_plotpy-完整用法參考)
8. [Octave 相容性修改說明](#8-octave-相容性修改說明)
9. [目錄結構](#9-目錄結構)

---

## 1. 系統需求

| 項目 | 版本 |
|------|------|
| 作業系統 | Linux / WSL2（Ubuntu 20.04+）|
| GNU Octave | ≥ 6.0（建議 8.x）|
| Python | ≥ 3.8 |
| SAR 前處理器 | ISCE2 / GAMMA / SNAP（至少一種）|
| SNAPHU | ≥ 2.0（相位展開）|
| TRIANGLE | 任意版本（Delaunay 三角化）|

---

## 2. 安裝

### 2-1. 取得本專案

```bash
git clone https://github.com/choin0207/StaMPS_octave_python.git ~/tools/StaMPS_octave_python
cd ~/tools/StaMPS_octave_python
```

### 2-2. 一鍵安裝（建議）

```bash
bash setup.sh
```

安裝腳本會依序完成：Octave + 套件安裝 → C/C++ 工具編譯 → Python 套件確認 → 環境變數寫入 `~/.bashrc`。

---

### 2-3. 手動安裝（若需逐步控制）

#### Octave 與套件

```bash
sudo apt update
sudo apt install -y \
    octave \
    octave-signal \
    octave-parallel \
    octave-io

octave --version
# 預期輸出：GNU Octave, version 8.x.x
```

#### Python 繪圖套件

```bash
# conda 環境（建議）
conda install -c conda-forge numpy scipy matplotlib h5py

# 或 pip
pip install numpy scipy matplotlib h5py
```

#### 編譯 C/C++ 輔助工具

```bash
cd ~/tools/StaMPS_octave_python/src
make install
cd ..
```

編譯後的執行檔（`calamp`、`pscdem`、`selpsc_patch` 等）會安裝至 `bin/`。

---

## 3. 設定環境變數

### 3-1. 載入設定

每次開啟終端機前執行（或寫入 `~/.bashrc` 永久生效）：

```bash
source ~/tools/StaMPS_octave_python/StaMPS_CONFIG.bash
```

寫入 `~/.bashrc`（只需做一次）：

```bash
echo 'source ~/tools/StaMPS_octave_python/StaMPS_CONFIG.bash' >> ~/.bashrc
source ~/.bashrc
```

### 3-2. 確認設定正確

執行以下指令，確認每一項均通過：

```bash
# 確認 STAMPS 路徑
echo $STAMPS
# 預期：/home/<user>/tools/StaMPS_octave_python

# 確認 Octave 搜尋路徑
echo $OCTAVE_PATH
# 預期：/home/<user>/tools/StaMPS_octave_python/matlab:...

# 確認 bin/ 在 PATH 中
which mt_prep_gamma
# 預期：/home/<user>/tools/StaMPS_octave_python/bin/mt_prep_gamma

# 確認 Octave 可正確載入 StaMPS 函數
octave --no-gui --quiet --eval "addpath(getenv('STAMPS')+'/matlab'); disp(which('stamps'))"
# 預期：.../matlab/stamps.m
```

### 3-3. `StaMPS_CONFIG.bash` 內容說明

```bash
export STAMPS=~/tools/StaMPS_octave_python    # StaMPS 根目錄
export PATH=$STAMPS/bin:$PATH                  # bin/ 加入 PATH
export OCTAVE_PATH=$STAMPS/matlab:...          # .m 檔案搜尋路徑（等同 MATLABPATH）
export PYTHONPATH=$STAMPS/python:...           # Python 模組路徑
export LC_NUMERIC=en_US.UTF-8                  # 確保數字格式正確
```

> **WSL2 使用者**：若需存取 Windows 檔案，路徑使用 `/mnt/c/Users/<name>/...`。

---

## 4. 執行 StaMPS

以下以 **ISCE2 + Sentinel-1** 工作流為例（GAMMA 流程類似）。

### 4-1. 前置：準備 InSAR 疊加資料

ISCE2 處理完成後，執行 StaMPS 資料準備：

```bash
cd /path/to/your/insar_project

# 設定處理器類型（isce / gamma / snap）
echo "isce" > processor.txt

# 準備 PS 候選像素（rms_threshold 通常 0.4~0.6）
mt_prep_gamma <master_date_YYYYMMDD> <insar_data_dir> <rms_threshold>

# 例：
mt_prep_gamma 20200101 /data/insar/toushe 0.4 1 1 50 50
```

### 4-2. 建立補丁清單

```bash
# 若資料量小，直接在根目錄處理（不分補丁）
# 若資料量大，建立補丁（patch）清單
patch_list=$(ls -d PATCH_*)
echo "$patch_list" > patch.list
```

### 4-3. 執行 stamps(1, 8)

```bash
# 進入處理目錄（或 PATCH_1/）
cd /path/to/your/insar_project

# 執行全部 8 個步驟
octave --no-gui --quiet << 'EOF'
stamps(1, 8)
EOF
```

各步驟說明：

| 步驟 | 函數 | 說明 | 典型耗時 |
|------|------|------|----------|
| 1 | `ps_load_initial` | 載入 PS 候選像素資料 | 1–5 分 |
| 2 | `ps_est_gamma_quick` | 估計相干性（γ）| 10–60 分 |
| 3 | `ps_select` | 選擇 PS 像素 | 5–30 分 |
| 4 | `ps_weed` | 去除鄰近像素 | 5–20 分 |
| 5 | `ps_correct_phase` | 包裹相位校正 | 2–10 分 |
| 6 | `ps_unwrap` | 相位展開（呼叫 SNAPHU）| 10–120 分 |
| 7 | `ps_calc_scla` | 估計 DEM 誤差 | 5–30 分 |
| 8 | `ps_scn_filt` | 空間相關噪音濾波 | 5–30 分 |

### 4-4. 分步執行（除錯用）

```bash
# 只跑步驟 1 到 3
octave --no-gui --quiet << 'EOF'
stamps(1, 3)
EOF

# 從步驟 4 繼續到 8
octave --no-gui --quiet << 'EOF'
stamps(4, 8)
EOF

# 從上次中斷點繼續（step 0 = 自動偵測）
octave --no-gui --quiet << 'EOF'
stamps(0, 8)
EOF
```

### 4-5. 合併補丁

若使用多補丁處理：

```bash
cd /path/to/your/insar_project   # 回到根目錄

octave --no-gui --quiet << 'EOF'
ps_merge_patches
EOF
```

### 4-6. 調整參數（選用）

```bash
# 在 Octave 中查詢/設定處理參數
octave --no-gui --quiet << 'EOF'
getparm('small_baseline_flag')
setparm('filter_grid_size', 50)
setparm('clap_alpha', 1.0)
EOF
```

常用參數一覽：

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `filter_grid_size` | 50 | 空間濾波網格大小（公尺）|
| `clap_alpha` | 1.0 | CLAP 濾波強度 |
| `unwrap_method` | `'snaphu'` | 相位展開方法 |
| `drop_ifg_index` | `[]` | 要排除的干涉圖索引 |
| `small_baseline_flag` | `'n'` | 是否為小基線模式 |

---

## 5. 畫圖（ps_plot.py）

`python/ps_plot.py` 是 `ps_plot.m` 的 Python 重寫版，支援相同的資料類型與互動功能。

### 5-1. 基本速度圖

```bash
cd /path/to/PATCH_1   # 或合併後的根目錄

# 平均 LOS 速度圖（白色背景，預設）
python $STAMPS/python/ps_plot.py v

# 去 DEM 誤差後的速度圖（最常用）
python $STAMPS/python/ps_plot.py v-d

# 黑色背景
python $STAMPS/python/ps_plot.py v-d --bg 0

# 自訂色帶範圍（mm/yr）
python $STAMPS/python/ps_plot.py v-d --lims -20 20

# 指定空間範圍
python $STAMPS/python/ps_plot.py v-d --lon-rg 120.8 121.2 --lat-rg 23.9 24.3
```

### 5-2. 互動時間序列（點擊地圖）

```bash
# 先產生時間序列資料（在 Octave 中跑一次）
octave --no-gui --quiet << 'EOF'
ps_plot('v-d', -1)   % background=-1 表示輸出 .mat 不畫圖
EOF

# 開啟互動視窗：點擊地圖上任意 PS 點 → 右側顯示時間序列
python $STAMPS/python/ps_plot.py v-d --ts
```

互動操作說明：
- **左鍵點擊地圖** → 以「Radius」為半徑，平均附近 PS 點的時間序列
- **Radius 輸入框** → 調整搜尋半徑（公尺，預設 100 m）
- **TS Plot 按鈕** → 重新選點
- **TS Double Diff 按鈕** → 選兩點做差分時間序列

### 5-3. 干涉圖相位圖

```bash
# 所有包裹相位干涉圖（多圖排列）
python $STAMPS/python/ps_plot.py w

# 去 DEM 誤差的包裹相位
python $STAMPS/python/ps_plot.py w-d

# 展開相位（所有干涉圖）
python $STAMPS/python/ps_plot.py u

# 展開相位去 DEM 誤差
python $STAMPS/python/ps_plot.py u-d

# 只看第 3、5、7 張干涉圖
python $STAMPS/python/ps_plot.py w --ifg-list 3 5 7

# 每排顯示 4 張
python $STAMPS/python/ps_plot.py w --n-x 4
```

### 5-4. 其他資料類型

```bash
# 地形高程
python $STAMPS/python/ps_plot.py hgt

# DEM 誤差（rad/m）
python $STAMPS/python/ps_plot.py d

# 速度標準差
python $STAMPS/python/ps_plot.py vs
```

### 5-5. 存圖（不顯示視窗）

```bash
mkdir -p output_data

# 存成 PNG（200 dpi）
python $STAMPS/python/ps_plot.py v-d --save output_data/velocity.png

# 批次存所有常用圖
for vtype in v v-d hgt d; do
    python $STAMPS/python/ps_plot.py $vtype \
        --bg 1 --lims -20 20 \
        --save output_data/${vtype//\//_}.png
done
```

### 5-6. Python API 呼叫

```python
import sys
sys.path.insert(0, '/path/to/StaMPS_octave_python/python')
from ps_plot import PSPlot

p = PSPlot(work_dir='/path/to/PATCH_1')

# 速度圖
p.plot('v-d', bg=1, lims=[-20, 20])

# 互動時間序列
p.plot('v-d', ts=True)

# 存圖
p.plot('v-d', bg=0, lims=[-30, 30], save='velocity_black.png')

# 所有包裹相位干涉圖，每排 5 張
p.plot('w', n_x=5, textsize=8)
```

### 5-7. 支援的繪圖類型完整列表

| 類型 | 說明 | 單位 |
|------|------|------|
| `v` | 平均 LOS 速度 | mm/yr |
| `V` | 由 SB 反演的 SM 速度 | mm/yr |
| `vs` | 速度標準差 | mm/yr |
| `v-d` | 速度（去 DEM 誤差）| mm/yr |
| `v-o` | 速度（去軌道斜坡）| mm/yr |
| `v-do` | 速度（去 DEM 誤差 + 軌道）| mm/yr |
| `w` | 包裹相位 | rad |
| `w-d` | 包裹相位（去 DEM）| rad |
| `w-o` | 包裹相位（去軌道）| rad |
| `u` | 展開相位 | rad |
| `u-d` | 展開相位（去 DEM）| rad |
| `u-do` | 展開相位（去 DEM + 軌道）| rad |
| `usb` | SB 展開相位 | rad |
| `hgt` | 地形高程 | m |
| `d` | DEM 誤差 | rad/m |

---

## 6. 匯出 PS 點資料（export_ps）

`export_ps()` 將每個 PS 點的座標與數值輸出為 **CSV** 或 **TXT**，供 GMT、GIS 軟體或後續分析使用。

> **限制**：僅支援 1-D scalar 類型（velocity、hgt、d 等），不支援 phase 類型（w、u 等）。

### 6-1. 命令列匯出

```bash
cd /path/to/PATCH_1

# CSV（逗號分隔，含 header）← 預設
python $STAMPS/python/ps_plot.py v-d --export ps_velocity.csv

# TXT（空格分隔，GMT 可直接 pipe）
python $STAMPS/python/ps_plot.py v-d --export ps_velocity.txt --fmt txt

# 不含 header（方便 GMT/awk 直接處理）
python $STAMPS/python/ps_plot.py v-d --export ps_velocity.txt --fmt txt --no-header

# 只匯出特定地理範圍
python $STAMPS/python/ps_plot.py v-d --export crop.csv \
    --lon-rg 120.8 121.2 --lat-rg 23.9 24.3

# 同時畫圖並匯出（兩者獨立執行）
python $STAMPS/python/ps_plot.py v-d --save velocity.png --export ps_velocity.csv

# 其他可匯出的類型
python $STAMPS/python/ps_plot.py hgt --export ps_height.csv
python $STAMPS/python/ps_plot.py d   --export ps_dem_error.csv
python $STAMPS/python/ps_plot.py vs  --export ps_vel_std.csv
```

### 6-2. 輸出格式

**CSV（預設）：**
```
lon,lat,v_d_mmPyr
121.043210,24.123456,-3.2150
121.044567,24.124789,1.8820
...
```

**TXT（空格）：**
```
lon lat v_d_mmPyr
121.043210 24.123456 -3.2150
121.044567 24.124789  1.8820
...
```

欄位名稱規則：`<value_type>_<unit>`，例如：
| value_type | 欄位名稱 |
|---|---|
| `v-d` | `v_d_mmPyr` |
| `hgt` | `hgt_m` |
| `d` | `d_radPm` |
| `vs` | `vs_mmPyr_std_dev_` |

### 6-3. Python API 匯出

```python
from ps_plot import PSPlot, export_ps_csv

p = PSPlot(work_dir='/path/to/PATCH_1')

# CSV
n = p.export_ps('v-d', 'ps_velocity.csv')
print(f'{n} PS points exported')

# TXT，不含 header
p.export_ps('v-d', 'ps_velocity.txt', fmt='txt', no_header=True)

# 空間裁切
p.export_ps('v-d', 'crop.csv', lon_rg=[120.8, 121.2], lat_rg=[23.9, 24.3])

# 模組函數（不需實例化）
export_ps_csv(work_dir='.', value_type='v-d', out_path='ps_v.csv')
```

### 6-4. GMT 使用範例

```bash
# 匯出無 header 的 TXT，直接 pipe 給 GMT
python $STAMPS/python/ps_plot.py v-d \
    --export /dev/stdout --fmt txt --no-header | \
    gmt psxy -R120/122/23/25 -JM15c -Sc0.05c -Cvel.cpt -Ba > vel.ps
```

---

## 7. ps_plot.py 完整用法參考

`python/ps_plot.py` 的 docstring 完整對應原始 `ps_plot.m` 的標頭說明，包含以下章節：

### 7-1. 支援的 value_type 完整列表

**速度類（1-D，輸出單位 mm/yr）**

| 類型 | 說明 |
|------|------|
| `v` | 平均 LOS 速度 |
| `V` | SB 反演的 SM 速度 |
| `vs` | 速度標準差 |
| `v-d` | 速度（去 DEM 誤差）← **最常用** |
| `v-o` | 速度（去軌道斜坡）|
| `v-do` | 速度（去 DEM 誤差 + 軌道）|
| `v-a` | 速度（去 APS 大氣）|
| `v-da` | 速度（去 DEM 誤差 + APS）|
| `v-dao` | 速度（去 DEM 誤差 + APS + 軌道）|
| `V-D` | SB 反演速度（去 DEM 誤差）|
| `V-DO` | SB 反演速度（去 DEM 誤差 + 軌道）|

**相位類（2-D，每張干涉圖一個子圖，單位 rad）**

| 類型 | 說明 |
|------|------|
| `w` | 包裹相位（干涉圖）|
| `p` | 空間濾波後的包裹相位 |
| `w-d` | 包裹相位（去 DEM 誤差）|
| `w-o` | 包裹相位（去軌道）|
| `w-do` | 包裹相位（去 DEM + 軌道）|
| `u` | 展開相位 |
| `u-d` | 展開相位（去 DEM）|
| `u-o` | 展開相位（去軌道）|
| `u-do` | 展開相位（去 DEM + 軌道）|
| `u-dm` | 展開相位（去 DEM + master AOE）|
| `usb` | SB 展開相位 |
| `usb-d` | SB 展開相位（去 DEM）|
| `usb-do` | SB 展開相位（去 DEM + 軌道）|

**其他類（1-D）**

| 類型 | 說明 | 單位 |
|------|------|------|
| `hgt` | 地形高程（DEM）| m |
| `d` | DEM 誤差 / 外觀誤差 | rad/m |
| `D` | SB 反演的 SM DEM 誤差 | rad/m |
| `dsb` | SB 模式的 DEM 誤差 | rad/m |

### 7-2. 與原始 MATLAB 函數對照

```
MATLAB:  ps_plot(value_type, plot_flag, lims, ref_ifg, ifg_list,
                 n_x, cbar_flag, textsize, textcolor, lon_rg, lat_rg, units)

Python:  p.plot(value_type, bg=plot_flag, lims=lims, ref_ifg=ref_ifg,
               ifg_list=ifg_list, n_x=n_x, cbar_flag=cbar_flag,
               textsize=textsize, lon_rg=lon_rg, lat_rg=lat_rg, units=units)
```

### 7-3. CLI 參數完整說明

| 參數 | 類型 | 預設 | 說明 |
|------|------|------|------|
| `value_type` | str | `v` | 資料類型（見上表）|
| `--bg` | int | `1` | 背景：0=黑，1=白 |
| `--lims MIN MAX` | float | auto | 色帶範圍（mm/yr 或 rad）|
| `--ref-ifg` | int | `0` | 參考干涉圖：0=master，-1=遞增 |
| `--ifg-list` | int... | all | 1-based 干涉圖索引 |
| `--n-x` | int | `0` | 子圖欄數（0=自動）|
| `--no-cbar` | flag | off | 隱藏 colorbar |
| `--textsize` | int | `10` | 日期標籤字體大小 |
| `--lon-rg` | float float | — | 經度範圍 |
| `--lat-rg` | float float | — | 緯度範圍 |
| `--ts` | flag | off | 互動時間序列模式 |
| `--save` | str | — | 存圖路徑（PNG/PDF）|
| `--export` | str | — | 匯出 CSV/TXT 路徑 |
| `--fmt` | str | `csv` | 匯出格式：`csv` 或 `txt` |
| `--no-header` | flag | off | 匯出時不含 header |
| `--work-dir` | str | `.` | .mat 資料所在目錄 |
| `--stamps-dir` | str | `$STAMPS` | StaMPS 安裝根目錄 |

### 7-4. 測試覆蓋（10 個測試，全通過）

```
tests/test_ps_plot.py
├── test_import                   ← PSPlot / load_mat / load_cpt 可正常匯入
├── test_load_cpt                 ← GMT .cpt 色帶解析正確
├── test_psplot_init              ← work_dir 路徑正確設定
├── test_getparm_default          ← parms.mat 不存在時回傳預設值
├── test_load_mat_v5              ← scipy.io 讀取 v5 .mat 格式
├── test_invalid_value_type       ← 不合法 value_type 拋出 ValueError
├── test_export_ps_csv            ← CSV 行數、header、欄位數正確
├── test_export_ps_txt            ← TXT 空格分隔、無逗號
├── test_export_ps_spatial_filter ← lon/lat 過濾確實減少輸出點數
└── test_export_ps_rejects_phase  ← w/u 類型正確拋出 ValueError
```

執行測試：
```bash
cd ~/tools/StaMPS_octave_python
python -m pytest tests/ -v
```

---

## 8. Octave 相容性修改說明

| 檔案 | 問題 | 修改方式 |
|------|------|----------|
| `azi_f_resample.m` | `fdesign.rsrc()` 需 Signal Processing Toolbox | 改用 `resample()`（`octave-signal`）|
| `batchjob.m` | `textread()` 已棄用 | 改用 `textscan()` |
| `ps_select.m` | `parfor` 需 Parallel Computing Toolbox | 加入 `pkg load parallel` |
| `ps_est_gamma_quick.m` | 同上 | 同上 |
| `ps_scn_filt.m` | 同上 | 同上 |
| `ps_scn_filt_krig.m` | 同上 | 同上 |
| `bin/*`（14 個）| `matlab -nojvm -nosplash -nodisplay` | `octave --no-gui --quiet` |

詳細說明見 [`docs/octave_compat.md`](docs/octave_compat.md)。

---

## 9. 目錄結構

```
StaMPS_octave_python/
├── matlab/                  # Octave 相容版 .m 檔案（125 個，已 patch）
│   ├── stamps.m             # 主流程控制（步驟 1–8）
│   ├── ps_select.m          # PS 像素選擇（parallel patch）
│   ├── ps_est_gamma_quick.m # 相干性估計（parallel patch）
│   ├── ps_scn_filt.m        # 空間噪音濾波（parallel patch）
│   ├── ps_scn_filt_krig.m   # 克里金濾波（parallel patch）
│   ├── azi_f_resample.m     # 方位角重採樣（Signal Toolbox patch）
│   ├── batchjob.m           # 批次作業入口（textscan patch）
│   └── cptfiles/            # GMT 色帶（供 ps_plot.py 使用）
├── python/
│   ├── __init__.py
│   └── ps_plot.py           # ps_plot.m 的 matplotlib 完整改寫
├── bin/                     # Shell 腳本（matlab→octave 全數替換）
├── src/                     # C/C++ 原始碼（calamp、pscdem 等）
├── tests/
│   └── test_ps_plot.py      # pytest 測試（10 個，全通過）
├── docs/
│   └── octave_compat.md     # Octave 相容性技術細節
├── StaMPS_CONFIG.bash        # 環境變數設定檔
├── setup.sh                  # 一鍵安裝腳本
└── README.md
```

---

## 原始版本

- [StaMPS 官方版本](https://github.com/dbekaert/StaMPS)
- 基於 StaMPS 4.1-beta（Andy Hooper, David Bekaert et al.）
- 授權：GPL-2.0

## 貢獻

歡迎提交 PR，針對更多 MATLAB Toolbox 函數補充 Octave 相容替換方案。
