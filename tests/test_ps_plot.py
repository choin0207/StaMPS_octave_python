"""
tests/test_ps_plot.py — ps_plot.py 基本功能測試
執行：pytest tests/test_ps_plot.py -v
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

# ── 測試 import ───────────────────────────────────────────────────────────────
def test_import():
    import ps_plot
    assert hasattr(ps_plot, 'PSPlot')
    assert hasattr(ps_plot, 'load_mat')
    assert hasattr(ps_plot, 'load_cpt')


# ── 測試 load_cpt（GMT 色帶）────────────────────────────────────────────────
def test_load_cpt():
    from ps_plot import load_cpt, PSPlot
    import matplotlib.colors as mcolors

    stamps_dir = os.path.join(os.path.dirname(__file__), '..')
    cpt_path   = os.path.join(stamps_dir, 'matlab', 'cptfiles', 'GMT_jet.cpt')

    if os.path.exists(cpt_path):
        cmap = load_cpt(cpt_path)
        assert isinstance(cmap, mcolors.LinearSegmentedColormap), \
            "load_cpt 應回傳 LinearSegmentedColormap"
    else:
        pytest.skip(f"GMT_jet.cpt 不存在：{cpt_path}")


# ── 測試 PSPlot 初始化 ────────────────────────────────────────────────────────
def test_psplot_init(tmp_path):
    from ps_plot import PSPlot
    p = PSPlot(work_dir=str(tmp_path))
    assert p.work_dir == tmp_path.resolve()


# ── 測試 getparm（無 parms.mat 時回傳 default）───────────────────────────────
def test_getparm_default(tmp_path):
    from ps_plot import PSPlot
    p = PSPlot(work_dir=str(tmp_path))
    val = p.getparm('small_baseline_flag', 'n')
    assert val == 'n', f"Expected 'n', got {val!r}"


# ── 測試 load_mat（生成假 .mat 並讀取）──────────────────────────────────────
def test_load_mat_v5(tmp_path):
    import scipy.io as sio
    from ps_plot import load_mat

    test_file = str(tmp_path / 'test.mat')
    data_in = {'lonlat': np.array([[121.5, 24.1], [121.6, 24.2]]),
               'n_ps': np.array([[2]])}
    sio.savemat(test_file, data_in)

    data_out = load_mat(test_file)
    assert 'lonlat' in data_out, "lonlat key missing"
    assert data_out['lonlat'].shape == (2, 2), \
        f"lonlat shape mismatch: {data_out['lonlat'].shape}"


# ── 測試 _get_ph_all 對無效 value_type 的錯誤處理 ───────────────────────────
def test_invalid_value_type(tmp_path):
    import scipy.io as sio
    from ps_plot import PSPlot

    # 建立最小 ps2.mat
    sio.savemat(str(tmp_path / 'ps2.mat'), {
        'lonlat':    np.random.rand(100, 2),
        'n_ps':      np.array([[100]]),
        'n_ifg':     np.array([[10]]),
        'day':       np.arange(10, dtype=float),
        'master_day': np.array([[5.0]]),
        'xy':        np.random.rand(100, 2),
    })
    sio.savemat(str(tmp_path / 'parms.mat'), {
        'small_baseline_flag': np.array(['n'], dtype=object),
    })
    (tmp_path / 'psver').write_text('2')

    p = PSPlot(work_dir=str(tmp_path))
    p._load_ps_data()

    with pytest.raises(ValueError, match="Unsupported value_type"):
        p._get_ph_all('invalid_type_xyz')


# ── 執行測試 ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
