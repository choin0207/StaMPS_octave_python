# Octave 相容性說明

## 修改清單

### 1. `azi_f_resample.m` — Signal Processing Toolbox 替換

**問題：**
```matlab
fnyq = fdesign.rsrc(L, M);          % DSP System Toolbox
hfrac = design(fnyq, 'kaiserwin');   % Signal Processing Toolbox
buffer = upfirdn(patch_tmp, hfrac, L, M);
```

**修改後（Octave 相容）：**
```matlab
% 使用 Octave signal 套件的 resample()
buffer = resample(patch_tmp, L, M);
```

`resample()` 內部使用 Kaiser 窗 FIR 濾波器，功能等效。

---

### 2. `batchjob.m` — textread → textscan

**問題：**
```matlab
% textread 已在 MATLAB R2014b 標記為 deprecated
[p(1),...,p(12),therest] = textread('matbgparms.txt', '%s%s...%[^\n]');
```

**修改後：**
```matlab
fid_bj = fopen('matbgparms.txt', 'r');
raw_bj  = textscan(fid_bj, '%s%s%s%s%s%s%s%s%s%s%s%s%[^\n]', 1);
fclose(fid_bj);
for i_bj = 1:12; p{i_bj} = raw_bj{i_bj}{1}; end
```

`textscan` 在 MATLAB 與 Octave 均支援。

---

### 3. `parfor` 相關檔案

**問題：** `parfor` 需要 MATLAB Parallel Computing Toolbox。

**修改：** 在每個含 `parfor` 的函式頂端加入：
```matlab
if exist('OCTAVE_VERSION', 'builtin')
    try; pkg load parallel; catch; end
end
```

**涉及檔案：**
- `ps_select.m`
- `ps_est_gamma_quick.m`
- `ps_scn_filt.m`
- `ps_scn_filt_krig.m`

**安裝 Octave parallel 套件：**
```bash
sudo apt install octave-parallel
# 或在 Octave 內：
octave:1> pkg install -forge parallel
```

**注意：** 若 `parallel` 套件未安裝，Octave 會自動將 `parfor` 降級為 `for` 執行，結果相同但無並行加速。

---

### 4. `bin/` 腳本 — matlab → octave

**修改前：**
```bash
matlab -nojvm -nosplash -nodisplay < $STAMPS/matlab/batchjob.m
```

**修改後：**
```bash
octave --no-gui --quiet < $STAMPS/matlab/batchjob.m
```

**旗標對應表：**

| MATLAB 旗標 | Octave 等效 | 說明 |
|-------------|------------|------|
| `-nojvm` | `--no-gui` | 不啟動 Java/GUI |
| `-nosplash` | `--quiet` | 不顯示啟動畫面 |
| `-nodisplay` | `--no-gui` | 無顯示 |
| `-nodesktop` | `--no-gui` | 無桌面 |

---

## 未支援功能

| 功能 | 狀態 | 說明 |
|------|------|------|
| `ps_plot.m` GUI | ⛔ 由 `python/ps_plot.py` 取代 | matplotlib 實作 |
| Envisat 振盪器校正 | ✅ 無須改動 | 純數學運算 |
| TRAIN 大氣校正（APS）| ⚠️ 部分支援 | 需另外安裝 TRAIN |
| Google Earth 輸出 | ✅ | `gescatter.m` 相容 |

---

## 測試指令

```bash
# 確認 Octave 可讀 parms.mat
octave --no-gui --quiet <<'EOF'
load parms.mat
disp(small_baseline_flag)
EOF

# 確認 parfor 可用
octave --no-gui --quiet <<'EOF'
pkg load parallel
parfor i=1:4; disp(i); end
EOF

# 確認 resample 可用
octave --no-gui --quiet <<'EOF'
pkg load signal
x = randn(1000, 1);
y = resample(x, 3, 2);  % 2:3 重採樣
disp(length(y))
EOF
```
