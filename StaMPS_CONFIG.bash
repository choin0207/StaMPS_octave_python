#!/bin/bash
# StaMPS Octave + Python Edition — Environment Configuration
# Source this file: source ~/tools/StaMPS_octave_python/StaMPS_CONFIG.bash

# ── StaMPS root ───────────────────────────────────────────────────────────────
export STAMPS=~/tools/StaMPS_octave_python

# ── PATH: StaMPS bin/ ────────────────────────────────────────────────────────
export PATH=$STAMPS/bin:$PATH

# ── Octave: equivalent of MATLABPATH ─────────────────────────────────────────
# Octave searches OCTAVE_PATH for .m files
export OCTAVE_PATH=$STAMPS/matlab:${OCTAVE_PATH:-}

# ── Python ps_plot ────────────────────────────────────────────────────────────
export PYTHONPATH=$STAMPS/python:${PYTHONPATH:-}

# ── SAR 前處理軟體路徑（請依實際路徑調整）────────────────────────────────────
# ISCE2
if [ -d "$HOME/miniconda3/envs/isce2" ]; then
    export ISCE_HOME=$HOME/miniconda3/envs/isce2
fi

# GAMMA（若有安裝）
# export GAMMA_HOME=/usr/local/gamma

# TRIANGLE（Delaunay 三角化）
if [ -f "$HOME/tools/triangle/triangle" ]; then
    export PATH=$HOME/tools/triangle:$PATH
fi

# SNAPHU（相位展開）
if [ -f "$HOME/tools/snaphu/bin/snaphu" ]; then
    export PATH=$HOME/tools/snaphu/bin:$PATH
fi

# ── Locale（確保數字格式正確）────────────────────────────────────────────────
export LC_NUMERIC=en_US.UTF-8
export LC_TIME=en_US.UTF-8

# ── 確認 Octave 可用 ─────────────────────────────────────────────────────────
if command -v octave &>/dev/null; then
    echo "[StaMPS] Octave: $(octave --version 2>&1 | head -1)"
else
    echo "[StaMPS] WARNING: Octave not found. Install: sudo apt install octave"
fi

echo "[StaMPS] STAMPS=$STAMPS"
echo "[StaMPS] OCTAVE_PATH=$OCTAVE_PATH"
