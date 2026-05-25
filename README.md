# StaMPS Octave + Python Edition

> **StaMPS 4.1-beta** 的開源化移植版本，將 MATLAB 依賴替換為 **GNU Octave**（計算核心）與 **Python/matplotlib**（視覺化），完全免費、免授權。

---

## 🎯 目標

| 原始 StaMPS | 本版本 |
|-------------|--------|
| MATLAB（需授權）| **GNU Octave**（免費） |
| MATLAB Parallel Toolbox | `octave-parallel` 套件 |
| MATLAB Signal Processing Toolbox | Octave `signal` 套件 |
| `ps_plot.m`（MATLAB 繪圖）| **`python/ps_plot.py`**（matplotlib） |

---

## 📦 安裝

### 1. 安裝 Octave

```bash
sudo apt update
sudo apt install -y octave octave-signal octave-parallel
octave --version   # 確認 >= 6.0
```

### 2. 設定環境變數

```bash
# 加入 ~/.bashrc
source ~/tools/StaMPS_octave_python/StaMPS_CONFIG.bash
```

### 3. 安裝 Python 繪圖依賴

```bash
pip install numpy scipy matplotlib h5py
# 或使用 conda（建議）
conda install numpy scipy matplotlib h5py
```

### 4. 編譯 C/C++ 工具

```bash
cd ~/tools/StaMPS_octave_python/src
make install
```

---

## 🚀 使用方式

### 計算流程（原本 MATLAB → 現在 Octave）

```bash
# 準備資料（與原 StaMPS 相同）
mt_prep_gamma <master_date> <datadir> <rms_threshold>

# 執行 StaMPS 步驟 1–8
octave --no-gui --quiet << 'EOF'
stamps(1, 8)
EOF

# 合併補丁
octave --no-gui --quiet << 'EOF'
ps_merge_patches
EOF
```

### 繪圖（Python 版 ps_plot）

```bash
cd <PATCH_1_directory>

# 速度圖（等同 ps_plot('v-d')）
python ~/tools/StaMPS_octave_python/python/ps_plot.py v-d

# 黑色背景
python ps_plot.py v-d --bg 0

# 自訂色帶範圍
python ps_plot.py v-d --lims -20 20

# 互動時間序列（點擊地圖看 TS）
python ps_plot.py v-d --ts

# 包裹相位所有干涉圖
python ps_plot.py w

# 存圖不顯示視窗
python ps_plot.py v-d --save output_data/velocity.png
```

### Python API 方式

```python
from python.ps_plot import PSPlot

p = PSPlot(work_dir='/path/to/PATCH_1')

# 速度圖
p.plot('v-d', bg=1, lims=[-20, 20])

# 互動時間序列
p.plot('v-d', ts=True)

# 存圖
p.plot('v-d', save='velocity_map.png')
```

---

## 📂 目錄結構

```
StaMPS_octave_python/
├── matlab/              # Octave 相容的 .m 檔案（125 個，已 patch）
│   ├── stamps.m         # 主流程
│   ├── ps_select.m      # PS 選擇（已加 parallel 套件載入）
│   ├── ps_scn_filt.m    # 空間噪音濾波
│   ├── azi_f_resample.m # 方位角重採樣（已移除 Signal Toolbox）
│   ├── batchjob.m       # 批次作業（textread→textscan）
│   └── cptfiles/        # GMT 色帶檔案
├── python/
│   └── ps_plot.py       # matplotlib GUI 繪圖（替代 ps_plot.m）
├── bin/                 # Shell 腳本（matlab→octave 已替換）
├── src/                 # C/C++ 原始碼
├── tests/               # 測試腳本
├── docs/
│   └── octave_compat.md # Octave 相容性說明
├── StaMPS_CONFIG.bash   # 環境變數設定
└── setup.sh             # 一鍵安裝腳本
```

---

## 🔧 Octave 相容性修改說明

| 檔案 | 問題 | 修改方式 |
|------|------|----------|
| `azi_f_resample.m` | `fdesign.rsrc()` 需要 Signal Processing Toolbox | 改用 Octave `resample()` |
| `batchjob.m` | `textread()` 已棄用 | 改用 `textscan()` |
| `ps_select.m` | `parfor` 需要 Parallel Computing Toolbox | 加入 `pkg load parallel` |
| `ps_est_gamma_quick.m` | 同上 | 同上 |
| `ps_scn_filt.m` | 同上 | 同上 |
| `ps_scn_filt_krig.m` | 同上 | 同上 |
| `bin/*` | 所有 `matlab` 指令 | 替換為 `octave --no-gui --quiet` |

---

## 🎨 ps_plot.py 支援的繪圖類型

| 類型 | 說明 |
|------|------|
| `v`, `V` | 平均 LOS 速度（mm/yr）|
| `vs`, `Vs` | 速度標準差 |
| `v-d`, `v-do` | 速度（去 DEM 誤差）|
| `w` | 包裹相位（干涉圖）|
| `u`, `u-d`, `u-do` | 展開相位 |
| `hgt` | 地形高程 |
| `d`, `D` | DEM 誤差（rad/m）|
| `--ts` | 互動點擊時間序列 |

---

## 📊 效能比較

| 環境 | stamps(1,8) 速度 | 費用 |
|------|-----------------|------|
| MATLAB R2019b | 基準 | 授權費用 |
| GNU Octave 8.x | ~1.2x 慢 | **免費** |
| Octave + parallel | ~0.9x（近似）| **免費** |

---

## 📖 原始版本

- [StaMPS 官方版本](https://github.com/dbekaert/StaMPS)
- 基於 StaMPS 4.1-beta（Andy Hooper et al.）
- 授權：GPL-2.0

---

## 🤝 貢獻

歡迎提交 PR 針對更多 MATLAB Toolbox 函數的 Octave 相容替換。
