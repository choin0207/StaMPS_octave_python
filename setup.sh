#!/bin/bash
# setup.sh — 一鍵安裝 StaMPS Octave + Python Edition
# Usage: bash setup.sh

set -e
echo "========================================"
echo " StaMPS Octave + Python — Setup"
echo "========================================"

# ── 1. 安裝 Octave ────────────────────────────────────────────────────────────
echo ""
echo "[1/4] 安裝 GNU Octave 與套件..."
if command -v octave &>/dev/null; then
    echo "      Octave 已安裝: $(octave --version 2>&1 | head -1)"
else
    sudo apt update
    sudo apt install -y octave octave-signal octave-parallel octave-io
    echo "      Octave 安裝完成"
fi

# ── 2. 編譯 C/C++ 工具 ───────────────────────────────────────────────────────
echo ""
echo "[2/4] 編譯 C/C++ 工具 (src/)..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -d "$SCRIPT_DIR/src" ]; then
    cd "$SCRIPT_DIR/src"
    if make install 2>&1; then
        echo "      編譯成功"
    else
        echo "      WARNING: 編譯失敗，請手動執行 cd src && make install"
    fi
    cd "$SCRIPT_DIR"
else
    echo "      src/ 目錄不存在，跳過"
fi

# ── 3. 安裝 Python 套件 ───────────────────────────────────────────────────────
echo ""
echo "[3/4] 確認 Python 繪圖套件..."
python3 -c "import numpy, scipy, matplotlib, h5py; print('      numpy scipy matplotlib h5py: OK')" 2>/dev/null || {
    echo "      安裝 Python 套件..."
    pip install numpy scipy matplotlib h5py --quiet
}

# ── 4. 環境變數 ───────────────────────────────────────────────────────────────
echo ""
echo "[4/4] 設定環境變數..."
BASHRC="$HOME/.bashrc"
CONFIG_LINE="source $SCRIPT_DIR/StaMPS_CONFIG.bash"

if grep -qF "$CONFIG_LINE" "$BASHRC" 2>/dev/null; then
    echo "      StaMPS_CONFIG.bash 已在 .bashrc 中"
else
    echo "" >> "$BASHRC"
    echo "# StaMPS Octave + Python" >> "$BASHRC"
    echo "$CONFIG_LINE" >> "$BASHRC"
    echo "      已加入 .bashrc: $CONFIG_LINE"
fi

echo ""
echo "========================================"
echo " 安裝完成！"
echo "========================================"
echo ""
echo "請執行以下指令啟用環境："
echo "  source ~/.bashrc"
echo ""
echo "驗證："
echo "  octave --version"
echo "  python3 $SCRIPT_DIR/python/ps_plot.py --help"
echo ""
echo "使用範例："
echo "  cd <PATCH_1 目錄>"
echo "  octave --no-gui --quiet <<< \"stamps(1,8)\""
echo "  python3 $SCRIPT_DIR/python/ps_plot.py v-d --ts"
