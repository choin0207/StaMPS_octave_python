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


# ── export_ps 測試 ────────────────────────────────────────────────────────────
def test_export_ps_csv(tmp_path):
    """export_ps('v-d') 應輸出包含 lon/lat/v-d 欄位的 CSV，行數等於 PS 點數。"""
    import scipy.io as sio
    from ps_plot import PSPlot
    import numpy as np

    n_ps = 50
    sio.savemat(str(tmp_path / 'ps2.mat'), {
        'lonlat':    np.column_stack([
                         np.random.uniform(120.9, 121.1, n_ps),
                         np.random.uniform(24.0,  24.2,  n_ps)]),
        'n_ps':      np.array([[n_ps]]),
        'n_ifg':     np.array([[10]]),
        'day':       np.arange(10, dtype=float) + 736000,
        'master_day': np.array([[736005.0]]),
        'xy':        np.random.rand(n_ps, 2),
    })
    sio.savemat(str(tmp_path / 'mv2.mat'), {
        'mv': np.random.uniform(-0.02, 0.02, n_ps),   # m/yr
    })
    sio.savemat(str(tmp_path / 'parms.mat'), {
        'small_baseline_flag': np.array(['n'], dtype=object),
    })
    (tmp_path / 'psver').write_text('2')

    p      = PSPlot(work_dir=str(tmp_path))
    out    = tmp_path / 'ps_velocity.csv'
    n_out  = p.export_ps('v-d', str(out), fmt='csv')

    assert n_out == n_ps, f"Expected {n_ps} rows, got {n_out}"
    assert out.exists(), "CSV file not created"

    lines = out.read_text().splitlines()
    assert lines[0].startswith('lon,lat,'), f"Bad header: {lines[0]}"
    assert len(lines) == n_ps + 1, f"Expected {n_ps+1} lines, got {len(lines)}"

    # 確認第一筆資料可解析
    parts = lines[1].split(',')
    assert len(parts) == 3, f"Expected 3 columns, got {len(parts)}"
    float(parts[0]), float(parts[1]), float(parts[2])   # must not raise


def test_export_ps_txt(tmp_path):
    """export_ps txt 格式應輸出空格分隔，不含引號。"""
    import scipy.io as sio
    from ps_plot import PSPlot
    import numpy as np

    n_ps = 20
    sio.savemat(str(tmp_path / 'ps2.mat'), {
        'lonlat':    np.column_stack([
                         np.random.uniform(121.0, 121.1, n_ps),
                         np.random.uniform(24.0,  24.1,  n_ps)]),
        'n_ps':  np.array([[n_ps]]), 'n_ifg': np.array([[5]]),
        'day':   np.arange(5, dtype=float) + 736000,
        'master_day': np.array([[736002.0]]),
        'xy':    np.random.rand(n_ps, 2),
    })
    sio.savemat(str(tmp_path / 'mv2.mat'),
                {'mv': np.random.uniform(-0.01, 0.01, n_ps)})
    sio.savemat(str(tmp_path / 'parms.mat'),
                {'small_baseline_flag': np.array(['n'], dtype=object)})
    (tmp_path / 'psver').write_text('2')

    p   = PSPlot(work_dir=str(tmp_path))
    out = tmp_path / 'ps_v.txt'
    p.export_ps('v', str(out), fmt='txt')

    lines = out.read_text().splitlines()
    assert ' ' in lines[0], "TXT header should be space-separated"
    assert ',' not in lines[1], "TXT data row should not contain commas"


def test_export_ps_spatial_filter(tmp_path):
    """lon_rg / lat_rg 過濾應減少輸出點數。"""
    import scipy.io as sio
    from ps_plot import PSPlot
    import numpy as np

    n_ps = 100
    lons = np.random.uniform(120.0, 122.0, n_ps)
    lats = np.random.uniform(23.0,  25.0,  n_ps)
    sio.savemat(str(tmp_path / 'ps2.mat'), {
        'lonlat': np.column_stack([lons, lats]),
        'n_ps':   np.array([[n_ps]]), 'n_ifg': np.array([[5]]),
        'day':    np.arange(5, dtype=float) + 736000,
        'master_day': np.array([[736002.0]]),
        'xy':     np.random.rand(n_ps, 2),
    })
    sio.savemat(str(tmp_path / 'mv2.mat'),
                {'mv': np.random.uniform(-0.02, 0.02, n_ps)})
    sio.savemat(str(tmp_path / 'parms.mat'),
                {'small_baseline_flag': np.array(['n'], dtype=object)})
    (tmp_path / 'psver').write_text('2')

    p = PSPlot(work_dir=str(tmp_path))
    out_all  = tmp_path / 'all.csv'
    out_crop = tmp_path / 'crop.csv'

    n_all  = p.export_ps('v', str(out_all))
    n_crop = p.export_ps('v', str(out_crop),
                          lon_rg=[121.0, 121.5], lat_rg=[23.5, 24.5])

    assert n_crop < n_all, \
        f"Filtered export ({n_crop}) should be < full export ({n_all})"


def test_export_ps_rejects_phase(tmp_path):
    """export_ps 對 2-D (phase) 類型應拋出 ValueError。"""
    import scipy.io as sio
    from ps_plot import PSPlot
    import numpy as np
    import pytest

    n_ps, n_ifg = 30, 8
    sio.savemat(str(tmp_path / 'ps2.mat'), {
        'lonlat': np.random.rand(n_ps, 2),
        'n_ps':   np.array([[n_ps]]), 'n_ifg': np.array([[n_ifg]]),
        'day':    np.arange(n_ifg, dtype=float) + 736000,
        'master_day': np.array([[736003.0]]),
        'xy':     np.random.rand(n_ps, 2),
    })
    sio.savemat(str(tmp_path / 'rc2.mat'), {
        'ph_rc': np.exp(1j * np.random.rand(n_ps, n_ifg)),
    })
    sio.savemat(str(tmp_path / 'parms.mat'),
                {'small_baseline_flag': np.array(['n'], dtype=object)})
    (tmp_path / 'psver').write_text('2')

    p = PSPlot(work_dir=str(tmp_path))
    p._load_ps_data()
    with pytest.raises(ValueError, match="1-D"):
        p.export_ps('w', str(tmp_path / 'out.csv'))
