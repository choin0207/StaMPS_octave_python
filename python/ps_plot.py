#!/usr/bin/env python3
"""
ps_plot.py — Python rewrite of StaMPS ps_plot.m
=================================================================
Original MATLAB function by Andy Hooper, June 2006.
Python port: matplotlib-based GUI + CSV/TXT export.

DESCRIPTION
-----------
Plots and exports PS (Persistent Scatterer) values from StaMPS
output .mat files.  Equivalent to the MATLAB call:

    ps_plot(VALUE_TYPE, BACKGROUND, PHASE_LIMS, REF_IFG, ...)

COMMAND-LINE USAGE
------------------
    python ps_plot.py <value_type> [options]

PYTHON API USAGE
----------------
    from ps_plot import PSPlot

    p = PSPlot(work_dir='/path/to/PATCH_1')
    p.plot('v-d', bg=1, lims=[-20, 20])        # plot
    p.export_ps('v-d', 'ps_velocity.csv')       # export CSV

VALUE TYPES — VELOCITY (single map, unit: mm/yr)
-------------------------------------------------
    v          Mean LOS velocity (from Step 7 output mv.mat)
    V          Mean LOS velocity inverted from SB (when using SB mode)
    vs         Standard deviation of mean LOS velocity
    Vs         Std dev of mean LOS velocity (SB-inverted)
    v-d        Mean velocity minus smoothed DEM error  ← 最常用
    v-o        Mean velocity minus orbital ramps
    v-do       Mean velocity minus DEM error and orbital ramps
    v-a        Mean velocity minus tropospheric APS correction
    v-da       Mean velocity minus DEM error and APS
    v-dao      Mean velocity minus DEM error, APS, and orbital ramps
    V-D        (SB-inverted) velocity minus DEM error
    V-DO       (SB-inverted) velocity minus DEM error and orbital ramps

VALUE TYPES — PHASE (multi-frame, one subplot per interferogram)
-----------------------------------------------------------------
    w          Wrapped phase (reference-corrected interferograms)
    p          Spatially filtered wrapped phase
    w-d        Wrapped phase minus smoothed DEM error
    w-o        Wrapped phase minus orbital ramps
    w-do       Wrapped phase minus DEM error and orbital ramps
    u          Unwrapped phase
    u-d        Unwrapped phase minus DEM error
    u-o        Unwrapped phase minus orbital ramps
    u-do       Unwrapped phase minus DEM error and orbital ramps
    u-dm       Unwrapped phase minus DEM error and master AOE
    usb        Unwrapped phase (small baseline interferograms)
    usb-d      Unwrapped SB phase minus DEM error
    usb-do     Unwrapped SB phase minus DEM error and orbital ramps

VALUE TYPES — OTHER
-------------------
    hgt        Terrain height (DEM, metres)
    d          Spatially correlated look angle error (rad/m)
    D          Spatially correlated DEM error from SM inverted SB data
    m          Master atmosphere and orbit error phase

BACKGROUND OPTIONS (--bg)
--------------------------
    0    Black background, lon/lat axes
    1    White background, lon/lat axes  ← default

PARAMETERS
----------
    --bg          INT   Background: 0=black, 1=white (default: 1)
    --lims        MIN MAX  Colormap limits, e.g. --lims -20 20
    --ref-ifg     INT   Reference interferogram index (0=master, -1=incremental)
    --ifg-list    INT.. Subset of ifgs to plot, 1-based, e.g. --ifg-list 1 3 5
    --n-x         INT   Number of columns in subplot grid (0=auto)
    --no-cbar         Hide colorbar
    --textsize    INT   Font size for date labels (default: 10)
    --lon-rg      LON_MIN LON_MAX  Longitude range filter
    --lat-rg      LAT_MIN LAT_MAX  Latitude range filter
    --ts              Enable interactive time-series click mode
    --save        PATH  Save figure to file (PNG/PDF, e.g. velocity.png)
    --export      PATH  Export PS points to CSV/TXT (lon, lat, value)
    --fmt         STR   Export format: csv (default) or txt
    --work-dir    PATH  Directory with StaMPS .mat files (default: .)
    --stamps-dir  PATH  StaMPS root (for cptfiles/)

EXAMPLES — COMMAND LINE
-----------------------
    # 速度圖（白底，自動色帶）
    python ps_plot.py v-d

    # 速度圖（黑底，色帶 ±20 mm/yr）
    python ps_plot.py v-d --bg 0 --lims -20 20

    # 點擊地圖看時間序列
    python ps_plot.py v-d --ts

    # 只看特定地理範圍
    python ps_plot.py v-d --lon-rg 120.8 121.2 --lat-rg 23.9 24.3

    # 存圖不顯示視窗
    python ps_plot.py v-d --save velocity.png

    # 包裹相位干涉圖，每排 5 張
    python ps_plot.py w --n-x 5

    # 只顯示第 2、4、6 張干涉圖
    python ps_plot.py w --ifg-list 2 4 6

    # 匯出 PS 點為 CSV（lon, lat, los_mm_yr）
    python ps_plot.py v-d --export ps_velocity.csv

    # 匯出為空格分隔 TXT
    python ps_plot.py v-d --export ps_velocity.txt --fmt txt

    # 指定處理目錄
    python ps_plot.py v-d --work-dir /data/insar/PATCH_1

EXAMPLES — PYTHON API
---------------------
    from ps_plot import PSPlot, export_ps_csv

    p = PSPlot(work_dir='/path/to/PATCH_1')

    # 繪圖
    p.plot('v-d')
    p.plot('v-d', bg=0, lims=[-20, 20])
    p.plot('v-d', ts=True)                          # 互動 TS
    p.plot('w',   n_x=5, textsize=8)                # 干涉圖網格
    p.plot('v-d', save='output_data/vel.png')        # 存圖

    # 匯出 CSV
    p.export_ps('v-d', 'ps_velocity.csv')

    # 快速匯出函數（不需實例化）
    export_ps_csv(work_dir='.', value_type='v-d', out_path='ps_v.csv')

NOTES
-----
    - work_dir 預設為當前目錄（.）
    - .mat 格式：自動支援 MATLAB v5 與 v7.3（HDF5）
    - 時間序列互動（--ts）需先在 Octave/MATLAB 執行：
          ps_plot('v-d', -1)
      以產生 ps_plot_ts_v-d.mat 資料檔
    - 色帶使用 GMT CPT 色帶（cptfiles/），與原 ps_plot.m 一致

ORIGINAL MATLAB SIGNATURE
--------------------------
    function [h_fig, lims, ifg_data_RMSE, h_axes_all] = ...
        ps_plot(value_type, plot_flag, lims, ref_ifg, ifg_list, n_x, ...
                cbar_flag, textsize, textcolor, lon_rg, lat_rg, units)

    Equivalent Python call:
        p.plot(value_type, bg=plot_flag, lims=lims, ref_ifg=ref_ifg,
               ifg_list=ifg_list, n_x=n_x, cbar_flag=cbar_flag,
               textsize=textsize, lon_rg=lon_rg, lat_rg=lat_rg, units=units)

AUTHORS
-------
    Original MATLAB: Andy Hooper, David Bekaert et al. (Stanford / TU Delft)
    Python port: StaMPS Octave+Python Edition
    License: GPL-2.0

CHANGELOG
---------
    2024-xx  Initial Python port
             - matplotlib scatter plot (equivalent to ps_plot_ifg.m)
             - Interactive time-series click (equivalent to ts_plot.m)
             - GMT CPT colormap support (via cptfiles/)
             - export_ps(): output lon/lat/value to CSV or TXT
"""

import argparse
import csv
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Button, TextBox

try:
    import scipy.io as sio
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False

warnings.filterwarnings('ignore', category=RuntimeWarning)


# ══════════════════════════════════════════════════════════════════════════════
# Module-level helpers
# ══════════════════════════════════════════════════════════════════════════════

def load_mat(path):
    """
    Load a MATLAB .mat file (v5 or v7.3 HDF5).

    Parameters
    ----------
    path : str or Path

    Returns
    -------
    dict  — variable name → numpy array
    """
    path = str(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"MAT file not found: {path}")
    # Try scipy (v5 / v7)
    if HAS_SCIPY:
        try:
            return sio.loadmat(path, squeeze_me=True, struct_as_record=False)
        except Exception:
            pass
    # Try h5py (v7.3 HDF5)
    if HAS_H5PY:
        out = {}
        with h5py.File(path, 'r') as f:
            def _read(grp):
                res = {}
                for k, v in grp.items():
                    if isinstance(v, h5py.Dataset):
                        arr = v[()]
                        if arr.dtype.kind in ('U', 'S', 'O'):
                            arr = str(arr)
                        elif isinstance(arr, np.ndarray) and arr.ndim >= 2:
                            arr = arr.T
                        res[k] = arr
                    elif isinstance(v, h5py.Group):
                        res[k] = _read(v)
                return res
            out = _read(f)
        return out
    raise RuntimeError(
        f"Cannot load {path}: install scipy or h5py.\n"
        "  pip install scipy h5py"
    )


def load_cpt(cpt_path):
    """
    Parse a GMT .cpt colour palette file → matplotlib LinearSegmentedColormap.

    Falls back to RdYlBu_r on any parse error.
    """
    try:
        entries = []
        with open(cpt_path) as f:
            for line in f:
                line = line.strip()
                if not line or line[0] in ('#', 'B', 'F', 'N'):
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        z = float(parts[0])
                        r, g, b = float(parts[1]), float(parts[2]), float(parts[3])
                        entries.append((z, r / 255, g / 255, b / 255))
                    except ValueError:
                        continue
        if not entries:
            return plt.cm.RdYlBu_r
        entries.sort(key=lambda x: x[0])
        z0, z1 = entries[0][0], entries[-1][0]
        span = z1 - z0 or 1.0
        colors = [((z - z0) / span, (r, g, b)) for z, r, g, b in entries]
        return mcolors.LinearSegmentedColormap.from_list('cpt', colors, N=256)
    except Exception:
        return plt.cm.RdYlBu_r


def export_ps_csv(work_dir='.', value_type='v-d', out_path='ps_output.csv',
                  fmt='csv', lon_rg=None, lat_rg=None, stamps_dir=None,
                  no_header=False):
    """
    Convenience function: export PS points to CSV or TXT without instantiating PSPlot.

    Parameters
    ----------
    work_dir   : str   Directory containing StaMPS .mat files
    value_type : str   Value type to export (must be 1-D: v, v-d, hgt, d, …)
    out_path   : str   Output file path
    fmt        : str   'csv' (comma-separated) or 'txt' (space-separated)
    lon_rg     : list  [lon_min, lon_max] spatial filter, optional
    lat_rg     : list  [lat_min, lat_max] spatial filter, optional
    stamps_dir : str   StaMPS root (for CPT files), optional
    no_header  : bool  Omit header row if True

    Returns
    -------
    int  — number of PS points written
    """
    p = PSPlot(work_dir=work_dir, stamps_dir=stamps_dir)
    return p.export_ps(value_type, out_path, fmt=fmt,
                       lon_rg=lon_rg, lat_rg=lat_rg, no_header=no_header)


# ══════════════════════════════════════════════════════════════════════════════
# PSPlot — main class
# ══════════════════════════════════════════════════════════════════════════════

class PSPlot:
    """
    Python equivalent of StaMPS ps_plot.m.

    Loads StaMPS output .mat files from `work_dir` and provides:
      - plot()      : scatter-map visualisation (velocity, phase, DEM, …)
      - export_ps() : write lon / lat / value to CSV or TXT

    Parameters
    ----------
    work_dir   : str  Directory containing ps2.mat, mv2.mat, parms.mat, …
    stamps_dir : str  StaMPS installation root (for matlab/cptfiles/).
                      Auto-detected from $STAMPS env var if not given.
    """

    # ── value types that produce a 1-D result (one number per PS point) ───────
    _SCALAR_TYPES = {
        'v', 'V', 'vs', 'Vs', 'vdrop',
        'v-d', 'v-o', 'v-a', 'v-do', 'v-da', 'v-dao', 'v-s', 'v-so',
        'V-D', 'V-O', 'V-DO', 'Vs-d', 'Vs-o', 'Vs-do',
        'vs-d', 'vs-o', 'vs-do', 'vs-da', 'vs-dao',
        'vdrop-d', 'vdrop-o', 'vdrop-do',
        'hgt', 'd', 'D', 'dsb', 'd-smooth',
    }

    def __init__(self, work_dir='.', stamps_dir=None):
        self.work_dir = Path(work_dir).resolve()
        if stamps_dir:
            self.stamps_dir = Path(stamps_dir)
        else:
            env = os.environ.get('STAMPS', '')
            self.stamps_dir = Path(env) if (env and Path(env).exists()) \
                              else Path(__file__).parent.parent
        self.cpt_dir = self.stamps_dir / 'matlab' / 'cptfiles'

        # lazily loaded
        self.ps    = None
        self.parms = None
        self.psver = 2

        # time-series cache
        self._ts_ph        = None
        self._ts_days      = None
        self._ts_value_type = None

    # ── internal path / load helpers ──────────────────────────────────────────

    def _matpath(self, name):
        p = self.work_dir / name
        return p if p.suffix else p.with_suffix('.mat')

    def _load(self, stem):
        """Load work_dir/<stem><psver>.mat"""
        return load_mat(self._matpath(f'{stem}{self.psver}'))

    def _load_parms(self):
        """Load parms.mat → self.parms dict."""
        try:
            raw = load_mat(self._matpath('parms'))
            self.parms = {k: v for k, v in raw.items() if not k.startswith('_')}
        except FileNotFoundError:
            self.parms = {}

    def getparm(self, key, default=None):
        """
        Equivalent to StaMPS getparm().
        Returns scalar Python value when possible.
        """
        if self.parms is None:
            self._load_parms()
        val = self.parms.get(key, default)
        if isinstance(val, np.ndarray) and val.size == 1:
            val = val.item()
        return val

    def _load_ps_data(self):
        """Load ps<ver>.mat → self.ps. Detect psver from psver file."""
        if self.ps is not None:
            return
        psver_file = self.work_dir / 'psver'
        if psver_file.exists():
            try:
                self.psver = int(psver_file.read_text().strip())
            except Exception:
                pass
        self._load_parms()
        raw = self._load('ps')
        self.ps = {k: v for k, v in raw.items() if not k.startswith('_')}
        # scalar conversion
        for key in ('n_ps', 'n_ifg', 'psver', 'master_ix'):
            if key in self.ps and isinstance(self.ps[key], np.ndarray):
                self.ps[key] = int(self.ps[key].flat[0])
        # 0-based master index
        if 'master_day' in self.ps and 'day' in self.ps:
            day = np.atleast_1d(self.ps['day']).flatten()
            md  = float(np.atleast_1d(self.ps['master_day']).flat[0])
            self.ps['master_ix0'] = int(np.sum(day < md))
        else:
            self.ps['master_ix0'] = 0

    # ── colormap helpers ──────────────────────────────────────────────────────

    def _get_cmap(self, name='jet'):
        """Return colormap: GMT CPT file if available, else matplotlib built-in."""
        cpt_names = {
            'GMT_jet':    'GMT_jet.cpt',
            'GMT_globe':  'GMT_globe.cpt',
            'GMT_gray':   'GMT_gray.cpt',
            'GMT_hot':    'GMT_hot.cpt',
            'GMT_cool':   'GMT_cool.cpt',
            'GMT_haxby':  'GMT_haxby.cpt',
            'default':    'GMT_jet.cpt',
        }
        scheme = self.getparm('plot_color_scheme', 'default')
        if isinstance(scheme, str) and scheme in cpt_names:
            f = self.cpt_dir / cpt_names[scheme]
            if f.exists():
                return load_cpt(f)
        try:
            return plt.get_cmap(name)
        except Exception:
            return plt.cm.jet

    def _vel_cmap(self):
        """Diverging blue-white-red for velocity."""
        return plt.cm.RdYlBu_r

    def _phase_cmap(self):
        """Cyclic HSV for wrapped phase."""
        return plt.cm.hsv

    # ── data loading by value_type ────────────────────────────────────────────

    def _get_ph_all(self, value_type):
        """
        Load and return (ph_all, units, fig_name, is_complex).

        ph_all shape:
          (n_ps,)        → 1-D  — velocity / hgt / DEM error
          (n_ps, n_ifg)  → 2-D  — wrapped / unwrapped phase per ifg
        """
        vt     = value_type.strip()
        vtl    = vt.lower()
        ps     = self.ps
        n_ps   = ps['n_ps']
        n_ifg  = ps['n_ifg']
        is_sb  = (str(self.getparm('small_baseline_flag', 'n')).strip().lower() == 'y')

        units      = ''
        fig_name   = vt
        is_complex = False

        # ── velocity (1-D) ────────────────────────────────────────────────────
        if vtl in ('v', 'vsb', 'v-d', 'v-do', 'v-dm', 'v-dmo',
                   'v-o', 'v-a', 'v-da', 'v-dao', 'v-s', 'v-so',
                   'v-doa', 'v-doas') or vtl.startswith('v'):
            mv = self._load('mv')
            ph_all = np.atleast_1d(mv['mv']).flatten() * 1000  # m/yr → mm/yr
            units  = 'mm/yr'

        elif vtl in ('vs', 'vs-d', 'vs-o', 'vs-do', 'vs-da', 'vs-dao') \
                or vtl.startswith('vs'):
            mv = self._load('mv')
            ph_all = np.atleast_1d(
                mv.get('mv_std', np.zeros(n_ps, dtype=float))
            ).flatten() * 1000
            units = 'mm/yr (std dev)'

        # ── topography (1-D) ──────────────────────────────────────────────────
        elif vtl == 'hgt':
            hgt    = self._load('hgt')
            ph_all = np.atleast_1d(hgt['hgt']).flatten()
            units  = 'm'

        # ── DEM / look-angle error (1-D) ──────────────────────────────────────
        elif vtl in ('d', 'dsb'):
            name   = 'scla_sb' if is_sb else 'scla'
            scla   = self._load(name)
            ph_all = np.atleast_1d(scla['K_ps_uw']).flatten()
            units  = 'rad/m'

        elif vtl in ('d-smooth',):
            name  = 'scla_smooth_sb' if is_sb else 'scla_smooth'
            scla  = self._load(name)
            ph_all = np.atleast_1d(
                scla.get('ph_scla', scla.get('K_ps_uw', np.zeros(n_ps)))
            ).flatten()
            units = 'rad/m'

        # ── wrapped phase (2-D, complex) ──────────────────────────────────────
        elif vtl in ('w', 'rc'):
            rc         = self._load('rc')
            ph_all     = rc['ph_rc']
            is_complex = True
            units      = 'rad'

        elif vtl == 'p':
            try:
                flt    = self._load('pfilt')
                ph_all = flt.get('ph_filt', flt.get('ph_rc'))
            except FileNotFoundError:
                ph_all = self._load('rc')['ph_rc']
            is_complex = True
            units      = 'rad'

        elif vtl == 'w-d':
            rc   = self._load('rc')
            name = 'scla_smooth_sb' if is_sb else 'scla_smooth'
            scla = self._load(name)
            ph_all     = rc['ph_rc'] * np.exp(-1j * scla['ph_scla'])
            is_complex = True
            units      = 'rad'

        elif vtl == 'w-o':
            rc   = self._load('rc')
            name = 'scla_smooth_sb' if is_sb else 'scla_smooth'
            scla = self._load(name)
            ph_all     = rc['ph_rc'] * np.exp(
                             -1j * (scla['ph_scla'] + scla.get('ph_ramp', 0)))
            is_complex = True
            units      = 'rad'

        elif vtl == 'w-do':
            rc   = self._load('rc')
            name = 'scla_smooth_sb' if is_sb else 'scla_smooth'
            scla = self._load(name)
            ph_all     = rc['ph_rc'] * np.exp(
                             -1j * (scla['ph_scla'] + scla.get('ph_ramp', 0)))
            is_complex = True
            units      = 'rad'

        # ── unwrapped phase (2-D, real) ───────────────────────────────────────
        elif vtl == 'u':
            phuw   = self._load('phuw')
            ph_all = phuw['ph_uw']
            units  = 'rad'

        elif vtl == 'u-d':
            phuw = self._load('phuw')
            scla = self._load('scla_sb' if is_sb else 'scla')
            ph_all = phuw['ph_uw'] - scla['ph_scla']
            units  = 'rad'

        elif vtl == 'u-o':
            phuw = self._load('phuw')
            scla = self._load('scla_smooth_sb' if is_sb else 'scla_smooth')
            ph_all = phuw['ph_uw'] - scla.get('ph_ramp', 0)
            units  = 'rad'

        elif vtl == 'u-do':
            phuw  = self._load('phuw')
            scla  = self._load('scla_sb' if is_sb else 'scla')
            scla2 = self._load('scla_smooth_sb' if is_sb else 'scla_smooth')
            ph_all = phuw['ph_uw'] - scla['ph_scla'] - scla2.get('ph_ramp', 0)
            units  = 'rad'

        elif vtl == 'u-dm':
            phuw  = self._load('phuw')
            scla  = self._load('scla_sb' if is_sb else 'scla')
            ph_all = (phuw['ph_uw']
                      - np.atleast_1d(scla['C_ps_uw']).reshape(-1, 1)
                      - scla['ph_scla'])
            ph_all[:, ps.get('master_ix0', 0)] = 0
            units  = 'rad'

        elif vtl == 'usb':
            phuw   = self._load('phuw_sb')
            ph_all = phuw['ph_uw']
            units  = 'rad'

        elif vtl == 'usb-d':
            phuw = self._load('phuw_sb')
            scla = self._load('scla_sb')
            ph_all = phuw['ph_uw'] - scla['ph_scla']
            units  = 'rad'

        elif vtl == 'usb-do':
            phuw  = self._load('phuw_sb')
            scla  = self._load('scla_sb')
            scla2 = self._load('scla_smooth_sb')
            ph_all = phuw['ph_uw'] - scla['ph_scla'] - scla2.get('ph_ramp', 0)
            units  = 'rad'

        # ── master AOE ────────────────────────────────────────────────────────
        elif vtl == 'm':
            try:
                scn    = self._load('scn')
                ph_all = scn.get('ph_scn_master', np.zeros((n_ps, n_ifg)))
            except FileNotFoundError:
                ph_all = np.zeros((n_ps, n_ifg))
            units = 'rad'

        else:
            supported = (
                'Velocity (1-D): v, V, vs, v-d, v-o, v-do, v-a, v-da, v-dao\n'
                'Phase   (2-D): w, p, w-d, w-o, w-do, u, u-d, u-o, u-do, u-dm, usb, usb-d, usb-do\n'
                'Other   (1-D): hgt, d, D, dsb'
            )
            raise ValueError(
                f"Unsupported value_type: '{value_type}'\n\n"
                f"Supported types:\n{supported}"
            )

        return ph_all, units, fig_name, is_complex

    # ══════════════════════════════════════════════════════════════════════════
    # export_ps — write lon / lat / value to CSV or TXT
    # ══════════════════════════════════════════════════════════════════════════

    def export_ps(self, value_type='v-d', out_path='ps_output.csv',
                  fmt='csv', lon_rg=None, lat_rg=None, no_header=False):
        """
        Export PS point coordinates and a scalar value to a plain-text file.

        Only works for value types that produce a 1-D result (one value per PS
        point): v, v-d, v-o, v-do, hgt, d, etc.  Phase types (w, u, …) are
        multi-frame and cannot be exported with this function.

        Parameters
        ----------
        value_type : str
            Data type to export.  Must be scalar (1-D) per PS point.
            Examples: 'v', 'v-d', 'hgt', 'd'
        out_path : str or Path
            Output file path.  Extension determines default format
            (.csv → csv, .txt → txt) unless `fmt` overrides.
        fmt : str
            'csv'  — comma-separated with header  (default)
            'txt'  — space-separated with header (GMT-compatible)
        lon_rg : list, optional
            [lon_min, lon_max] — export only PS within this longitude range
        lat_rg : list, optional
            [lat_min, lat_max] — export only PS within this latitude range
        no_header : bool
            If True, omit the header row (useful for direct GMT piping)

        Returns
        -------
        int  Number of PS points written

        Output columns
        --------------
        CSV:  lon, lat, <value_type>_<unit>
        TXT:  lon  lat  <value_type>_<unit>

        Examples
        --------
        # Command line
        python ps_plot.py v-d --export ps_velocity.csv
        python ps_plot.py v-d --export ps_velocity.txt --fmt txt
        python ps_plot.py hgt --export ps_height.csv

        # Python API
        p = PSPlot(work_dir='/path/to/PATCH_1')
        n = p.export_ps('v-d', 'ps_velocity.csv')
        print(f'{n} PS points exported')

        n = p.export_ps('v-d', 'ps_velocity.txt', fmt='txt', no_header=True)

        # Quick one-liner
        from ps_plot import export_ps_csv
        export_ps_csv(work_dir='.', value_type='v-d', out_path='ps_v.csv')
        """
        self._load_ps_data()

        # ── load data and validate it is 1-D ──────────────────────────────────
        ph_all, units, _, is_complex = self._get_ph_all(value_type)

        if ph_all.ndim != 1:
            raise ValueError(
                f"export_ps() only supports scalar (1-D) value types.\n"
                f"'{value_type}' returns shape {ph_all.shape}.\n"
                f"Use a velocity or hgt/d type, e.g. v, v-d, hgt, d."
            )

        # ── load coordinates ───────────────────────────────────────────────────
        lonlat = np.atleast_2d(self.ps['lonlat'])
        lon    = lonlat[:, 0]
        lat    = lonlat[:, 1]
        n_ps   = self.ps['n_ps']

        # ── spatial filter ─────────────────────────────────────────────────────
        mask = np.ones(n_ps, dtype=bool)
        if lon_rg:
            mask &= (lon >= lon_rg[0]) & (lon <= lon_rg[1])
        if lat_rg:
            mask &= (lat >= lat_rg[0]) & (lat <= lat_rg[1])
        # also drop NaN values
        mask &= np.isfinite(ph_all)

        lon_out = lon[mask]
        lat_out = lat[mask]
        val_out = ph_all[mask]
        n_out   = int(np.sum(mask))

        if n_out == 0:
            print(f'[export_ps] WARNING: 0 PS points match the filter — nothing written.')
            return 0

        # ── determine separator and column header ──────────────────────────────
        out_path = Path(out_path)
        # auto-detect from extension if fmt not explicitly given
        if fmt == 'csv' and out_path.suffix.lower() == '.txt':
            fmt = 'txt'

        col_name    = f'{value_type.replace("-", "_")}_{units.replace("/", "p").replace(" ", "_")}'
        sep         = ',' if fmt == 'csv' else ' '
        header_line = sep.join(['lon', 'lat', col_name])

        # ── write ──────────────────────────────────────────────────────────────
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', newline='') as fh:
            if not no_header:
                fh.write(header_line + '\n')
            for i in range(n_out):
                fh.write(f'{lon_out[i]:.6f}{sep}{lat_out[i]:.6f}{sep}{val_out[i]:.4f}\n')

        print(f'[export_ps] {n_out} PS points → {out_path}  ({fmt}, {units})')
        return n_out

    # ══════════════════════════════════════════════════════════════════════════
    # plot — main visualisation
    # ══════════════════════════════════════════════════════════════════════════

    def plot(self, value_type='v', bg=1, lims=None,
             ref_ifg=0, ifg_list=None, n_x=0,
             cbar_flag=0, textsize=10, lon_rg=None, lat_rg=None,
             units=None, ts=False, save=None):
        """
        Plot PS values.  Equivalent to ps_plot(value_type, bg, lims, …).

        Parameters
        ----------
        value_type : str   Data type (see module docstring for full list)
        bg         : int   Background: 0=black, 1=white (default)
        lims       : list  [min, max] colormap limits; None = auto (0.1–99.9 pct)
        ref_ifg    : int   Reference interferogram (0=master, -1=incremental)
        ifg_list   : list  1-based list of ifgs to plot; None = all
        n_x        : int   Subplot columns (0 = auto √N)
        cbar_flag  : int   0 = show colorbar (default), 1 = hide
        textsize   : int   Date label font size (default: 10)
        lon_rg     : list  [lon_min, lon_max] spatial crop
        lat_rg     : list  [lat_min, lat_max] spatial crop
        units      : str   Override units label on colorbar
        ts         : bool  Enable interactive time-series click mode
        save       : str   Path to save figure (PNG/PDF); None = display

        Returns
        -------
        matplotlib.figure.Figure or None
        """
        self._load_ps_data()
        ps   = self.ps
        n_ps = ps['n_ps']

        lonlat = np.atleast_2d(ps['lonlat'])
        lon    = lonlat[:, 0]
        lat    = lonlat[:, 1]

        mask = np.ones(n_ps, dtype=bool)
        if lon_rg:
            mask &= (lon >= lon_rg[0]) & (lon <= lon_rg[1])
        if lat_rg:
            mask &= (lat >= lat_rg[0]) & (lat <= lat_rg[1])

        try:
            ph_all, auto_units, fig_name, is_complex = self._get_ph_all(value_type)
        except Exception as e:
            print(f'[ps_plot] Error: {e}')
            raise

        if units is None:
            units = auto_units

        if ph_all.ndim == 1:
            return self._plot_single(
                ph_all, lon, lat, mask, lims, units, fig_name,
                bg, cbar_flag, textsize, ts, save, value_type)
        else:
            return self._plot_multi(
                ph_all, lon, lat, mask, lims, units, fig_name,
                bg, cbar_flag, textsize, ref_ifg, ifg_list,
                n_x, is_complex, save)

    # ── single-map plot (velocity / hgt / dem error) ──────────────────────────

    def _plot_single(self, data, lon, lat, mask, lims, units, fig_name,
                     bg, cbar_flag, textsize, ts, save, value_type):

        fc   = 'white' if bg == 1 else 'black'
        tc   = 'black' if bg == 1 else 'white'
        cmap = self._vel_cmap()

        vals  = data[mask]
        lon_m = lon[mask]
        lat_m = lat[mask]

        if lims is None:
            p01 = np.nanpercentile(vals, 0.1)
            p99 = np.nanpercentile(vals, 99.9)
            lims = [p01, p99]

        fig_h = 8 if ts else 7
        fig   = plt.figure(figsize=(10, fig_h), facecolor=fc)
        fig.canvas.manager.set_window_title(f'ps_plot — {fig_name}')

        if ts:
            ax_map = fig.add_axes([0.05, 0.15, 0.50, 0.78])
            ax_ts  = fig.add_axes([0.60, 0.15, 0.37, 0.78])
            self._setup_ts_panel(ax_ts, fig, fig_name, ax_map, lon, lat,
                                 data, value_type, fc, tc, textsize)
        else:
            ax_map = fig.add_axes([0.08, 0.08, 0.84, 0.88])

        ax_map.set_facecolor(fc)
        sc = ax_map.scatter(lon_m, lat_m, c=vals, cmap=cmap,
                            vmin=lims[0], vmax=lims[1],
                            s=1.5, linewidths=0, rasterized=True)
        ax_map.set_xlabel('Longitude', color=tc, fontsize=textsize)
        ax_map.set_ylabel('Latitude',  color=tc, fontsize=textsize)
        ax_map.set_title(fig_name,     color=tc, fontsize=textsize + 2,
                         fontweight='bold')
        ax_map.tick_params(colors=tc)
        ax_map.set_aspect('equal', adjustable='datalim')
        for sp in ax_map.spines.values():
            sp.set_edgecolor(tc)

        if cbar_flag == 0:
            cb = fig.colorbar(sc, ax=ax_map, orientation='vertical',
                              fraction=0.03, pad=0.02, shrink=0.8)
            cb.set_label(units, color=tc, fontsize=textsize)
            cb.ax.yaxis.set_tick_params(color=tc)
            plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=tc)

        print(f'ps_plot: Color range: {lims[0]:.4g} to {lims[1]:.4g} {units}')

        if save:
            out = Path(save)
            out.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(out, dpi=200, bbox_inches='tight', facecolor=fc)
            print(f'ps_plot: Saved → {out}')
        else:
            plt.show()
        return fig

    def _setup_ts_panel(self, ax_ts, fig, fig_name, ax_map,
                        lon, lat, vel_data, value_type, fc, tc, textsize):
        """Configure the time-series right panel and wire the click event."""
        ax_ts.set_facecolor(fc)
        ax_ts.tick_params(colors=tc)
        ax_ts.set_xlabel('Date', color=tc, fontsize=textsize)
        ax_ts.set_ylabel('Displacement (mm)', color=tc, fontsize=textsize)
        ax_ts.set_title('Click on map to see time series',
                        color=tc, fontsize=textsize)
        for sp in ax_ts.spines.values():
            sp.set_edgecolor(tc)

        btn_c = '#555' if fc == 'black' else '#ddd'
        ax_b1 = fig.add_axes([0.05, 0.04, 0.12, 0.06])
        ax_b2 = fig.add_axes([0.20, 0.04, 0.16, 0.06])
        ax_b3 = fig.add_axes([0.42, 0.04, 0.10, 0.06])
        ax_b4 = fig.add_axes([0.53, 0.04, 0.06, 0.06])
        self._btn_ts   = Button(ax_b1, 'TS Plot',        color=btn_c)
        self._btn_diff = Button(ax_b2, 'TS Double Diff.', color=btn_c)
        self._txt_lab  = TextBox(ax_b3, 'Radius (m)', initial='radius')
        self._txt_rad  = TextBox(ax_b4, '',           initial='100')

        self._ts_radius     = [100.0]
        self._ts_value_type = value_type

        def _upd_radius(txt):
            try:
                self._ts_radius[0] = float(txt)
            except ValueError:
                pass
        self._txt_rad.on_submit(_upd_radius)

        def _on_click(event):
            if event.inaxes != ax_map:
                return
            self._ts_click(event.xdata, event.ydata,
                           fig, ax_ts, tc, textsize, lon, lat)
        self._cid = fig.canvas.mpl_connect('button_press_event', _on_click)

    def _ts_click(self, lon0, lat0, fig, ax_ts, tc, textsize, lon_all, lat_all):
        """Map click handler: find nearby PS and plot their mean displacement."""
        ph_mm, dates = self._load_ts_data(self._ts_value_type)
        ax_ts.cla()
        ax_ts.set_facecolor(fig.get_facecolor())
        if ph_mm is None:
            ax_ts.set_title(
                'No time series data.\n'
                'Run ps_plot(\'v-d\', -1) in Octave/MATLAB first.',
                color=tc, fontsize=textsize - 1)
            fig.canvas.draw()
            return

        radius = self._ts_radius[0]
        dlat   = (lat_all - lat0) * 111_000
        dlon   = (lon_all - lon0) * 111_000 * np.cos(np.radians(lat0))
        dist   = np.hypot(dlat, dlon)

        in_r = dist <= radius
        if not np.any(in_r):
            ax_ts.set_title(f'No PS within {radius:.0f} m — enlarge radius',
                            color=tc, fontsize=textsize - 1)
            fig.canvas.draw()
            return

        ts_mean = np.nanmean(ph_mm[in_r, :], axis=0)
        ax_ts.plot(dates, ts_mean, 'o-', color='steelblue',
                   ms=4, lw=1.5, label=f'{np.sum(in_r)} PS, r={radius:.0f} m')
        ax_ts.axhline(0, color='gray', lw=0.8, ls='--')
        ax_ts.set_xlabel('Date',               color=tc, fontsize=textsize)
        ax_ts.set_ylabel('Displacement (mm)',  color=tc, fontsize=textsize)
        ax_ts.set_title(f'TS  lon={lon0:.4f}  lat={lat0:.4f}',
                        color=tc, fontsize=textsize)
        ax_ts.tick_params(colors=tc)
        ax_ts.legend(fontsize=textsize - 2)
        for sp in ax_ts.spines.values():
            sp.set_edgecolor(tc)
        try:
            fig.autofmt_xdate()
        except Exception:
            pass
        fig.canvas.draw()

    def _load_ts_data(self, value_type='v-d'):
        """
        Load time-series displacement (mm) per PS point.

        Priority:
          1. ps_plot_ts_<value_type>*.mat  (from ps_plot(..., -1) in Octave)
          2. phuw<ver>.mat converted to mm via wavelength
        """
        if self._ts_ph is not None and self._ts_value_type == value_type:
            return self._ts_ph, self._ts_days

        self._ts_value_type = value_type
        ph_mm, days = None, None

        # 1. look for pre-exported mat
        candidates = list(self.work_dir.glob(f'ps_plot_ts_{value_type}*.mat'))
        if candidates:
            dat   = load_mat(candidates[0])
            ph_mm = dat.get('ph_disp', dat.get('ph_mm'))
            days  = dat.get('day', self.ps.get('day'))

        # 2. fallback: phuw → mm
        if ph_mm is None:
            try:
                phuw  = self._load('phuw')
                lam   = float(self.getparm('lambda', 0.056) or 0.056) * 1000  # mm
                ph_mm = phuw['ph_uw'] / (4 * np.pi) * lam
                days  = self.ps.get('day')
            except FileNotFoundError:
                pass

        if ph_mm is None:
            self._ts_ph, self._ts_days = None, None
            return None, None

        # Convert MATLAB datenum → Python date
        if days is not None:
            from datetime import date
            days = np.atleast_1d(days).flatten()
            try:
                self._ts_days = [date.fromordinal(int(d) - 366) for d in days]
            except Exception:
                self._ts_days = np.arange(len(days))
        self._ts_ph = ph_mm
        return self._ts_ph, self._ts_days

    # ── multi-frame plot (interferograms) ─────────────────────────────────────

    def _plot_multi(self, ph_all, lon, lat, mask, lims, units, fig_name,
                    bg, cbar_flag, textsize, ref_ifg, ifg_list,
                    n_x, is_complex, save):
        from datetime import datetime

        ps    = self.ps
        fc    = 'white' if bg == 1 else 'black'
        tc    = 'black' if bg == 1 else 'white'
        cmap  = self._phase_cmap() if is_complex else self._vel_cmap()
        n_ifg = ph_all.shape[1]
        day   = np.atleast_1d(ps.get('day', np.arange(n_ifg))).flatten()

        if ifg_list is None:
            drop = np.atleast_1d(
                self.getparm('drop_ifg_index', np.array([]))
            ).flatten().astype(int)
            ifg_list = [i for i in range(n_ifg) if (i + 1) not in drop]
        else:
            ifg_list = [i - 1 for i in np.atleast_1d(ifg_list)]

        n_plot = len(ifg_list)
        if n_plot == 0:
            print('[ps_plot] No interferograms to plot.')
            return

        if n_x == 0:
            n_x = min(n_plot, max(1, int(np.ceil(np.sqrt(n_plot * 1.5)))))
        n_y = int(np.ceil(n_plot / n_x))

        fig, axes = plt.subplots(n_y, n_x, figsize=(3 * n_x, 3 * n_y),
                                 facecolor=fc, squeeze=False)
        fig.canvas.manager.set_window_title(f'ps_plot — {fig_name}')

        lon_m = lon[mask]
        lat_m = lat[mask]

        if is_complex:
            ph_disp  = np.angle(ph_all[mask, :])
            lims_use = [-np.pi, np.pi]
        else:
            ph_disp = ph_all[mask, :]
            mix0    = ps.get('master_ix0', 0)
            if ref_ifg > 0 and ref_ifg - 1 < ph_disp.shape[1]:
                ph_disp -= ph_disp[:, ref_ifg - 1:ref_ifg]
            elif ref_ifg == 0 and mix0 < ph_disp.shape[1]:
                ph_disp -= ph_disp[:, mix0:mix0 + 1]
            if lims is None:
                flat = ph_disp[:, ifg_list].ravel()
                flat = flat[np.isfinite(flat)]
                lims_use = (
                    [np.percentile(flat, 0.1), np.percentile(flat, 99.9)]
                    if len(flat) else [-1, 1]
                )
            else:
                lims_use = lims

        first_sc = None
        for pidx, ifg_idx in enumerate(ifg_list):
            row, col = pidx // n_x, pidx % n_x
            ax = axes[row, col]
            ax.set_facecolor(fc)
            sc = ax.scatter(lon_m, lat_m, c=ph_disp[:, ifg_idx], cmap=cmap,
                            vmin=lims_use[0], vmax=lims_use[1],
                            s=0.8, linewidths=0, rasterized=True)
            ax.set_aspect('equal', adjustable='datalim')
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_edgecolor(tc)
            if textsize != 0 and ifg_idx < len(day):
                try:
                    label = datetime.fromordinal(int(day[ifg_idx]) - 366
                                                ).strftime('%d %b %Y')
                except Exception:
                    label = str(ifg_idx + 1)
                ax.set_title(label, color=tc, fontsize=abs(textsize),
                             fontweight='bold', pad=2)
            if first_sc is None:
                first_sc = sc

        for pidx in range(n_plot, n_x * n_y):
            axes[pidx // n_x, pidx % n_x].set_visible(False)

        if cbar_flag == 0 and first_sc is not None:
            cb = fig.colorbar(first_sc, ax=axes.ravel().tolist(),
                              orientation='horizontal', fraction=0.02,
                              pad=0.02, shrink=0.6)
            cb.set_label(units, color=tc, fontsize=textsize)
            cb.ax.xaxis.set_tick_params(color=tc)
            plt.setp(plt.getp(cb.ax.axes, 'xticklabels'), color=tc)

        plt.suptitle(fig_name, color=tc, fontsize=textsize + 2, fontweight='bold')
        print(f'ps_plot: Color range: {lims_use[0]:.4g} to {lims_use[1]:.4g} {units}')

        if save:
            out = Path(save)
            out.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(out, dpi=200, bbox_inches='tight', facecolor=fc)
            print(f'ps_plot: Saved → {out}')
        else:
            plt.tight_layout()
            plt.show()
        return fig


# ══════════════════════════════════════════════════════════════════════════════
# Command-line interface
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        prog='ps_plot.py',
        description='ps_plot.py — Python rewrite of StaMPS ps_plot.m',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'VALUE TYPES\n'
            '-----------\n'
            '  Velocity (1-D, mm/yr): v  V  vs  v-d  v-o  v-do  v-a  v-da  v-dao\n'
            '                         V-D  V-DO  vs-d  vs-do\n'
            '  Phase    (2-D, rad):   w  p  w-d  w-o  w-do\n'
            '                         u  u-d  u-o  u-do  u-dm\n'
            '                         usb  usb-d  usb-do\n'
            '  Other    (1-D):        hgt  d  D  dsb\n\n'
            'EXAMPLES\n'
            '--------\n'
            '  python ps_plot.py v-d\n'
            '  python ps_plot.py v-d --bg 0 --lims -20 20\n'
            '  python ps_plot.py v-d --ts\n'
            '  python ps_plot.py v-d --save velocity.png\n'
            '  python ps_plot.py v-d --export ps_velocity.csv\n'
            '  python ps_plot.py w   --n-x 5\n'
            '  python ps_plot.py w   --ifg-list 1 3 5\n'
            '  python ps_plot.py hgt --export ps_height.txt --fmt txt\n'
        )
    )

    # positional
    parser.add_argument(
        'value_type', nargs='?', default='v',
        help='Value type to plot/export (default: v). See VALUE TYPES above.')

    # plot options
    plot_grp = parser.add_argument_group('Plot options')
    plot_grp.add_argument('--bg', type=int, default=1, metavar='INT',
        help='Background: 0=black, 1=white (default: 1)')
    plot_grp.add_argument('--lims', type=float, nargs=2, metavar=('MIN', 'MAX'),
        help='Colormap limits, e.g. --lims -20 20')
    plot_grp.add_argument('--ref-ifg', type=int, default=0, metavar='INT',
        help='Reference interferogram: 0=master (default), -1=incremental')
    plot_grp.add_argument('--ifg-list', type=int, nargs='+', metavar='INT',
        help='1-based interferogram indices to plot, e.g. --ifg-list 1 3 5')
    plot_grp.add_argument('--n-x', type=int, default=0, metavar='INT',
        help='Subplot columns (0=auto, default: 0)')
    plot_grp.add_argument('--no-cbar', action='store_true',
        help='Hide colorbar')
    plot_grp.add_argument('--textsize', type=int, default=10, metavar='INT',
        help='Font size for labels (default: 10)')
    plot_grp.add_argument('--lon-rg', type=float, nargs=2,
        metavar=('LON_MIN', 'LON_MAX'),
        help='Longitude range, e.g. --lon-rg 120.8 121.2')
    plot_grp.add_argument('--lat-rg', type=float, nargs=2,
        metavar=('LAT_MIN', 'LAT_MAX'),
        help='Latitude range, e.g. --lat-rg 23.9 24.3')
    plot_grp.add_argument('--ts', action='store_true',
        help='Interactive time-series click mode (velocity types only)')
    plot_grp.add_argument('--save', type=str, metavar='PATH',
        help='Save figure to file (PNG/PDF), e.g. --save velocity.png')

    # export options
    exp_grp = parser.add_argument_group('Export options (lon/lat/value to file)')
    exp_grp.add_argument('--export', type=str, metavar='PATH',
        help='Export PS points to CSV or TXT, e.g. --export ps_vel.csv')
    exp_grp.add_argument('--fmt', type=str, default='csv',
        choices=['csv', 'txt'],
        help="Export format: 'csv' (default) or 'txt' (space-separated)")
    exp_grp.add_argument('--no-header', action='store_true',
        help='Omit header row in exported file')

    # path options
    path_grp = parser.add_argument_group('Path options')
    path_grp.add_argument('--work-dir', type=str, default='.', metavar='PATH',
        help='Directory containing StaMPS .mat files (default: .)')
    path_grp.add_argument('--stamps-dir', type=str, default=None, metavar='PATH',
        help='StaMPS installation root (for cptfiles/). Default: $STAMPS env var')

    args = parser.parse_args()

    p = PSPlot(work_dir=args.work_dir, stamps_dir=args.stamps_dir)

    # export
    if args.export:
        p.export_ps(
            value_type = args.value_type,
            out_path   = args.export,
            fmt        = args.fmt,
            lon_rg     = args.lon_rg,
            lat_rg     = args.lat_rg,
            no_header  = args.no_header,
        )

    # plot (always runs unless --export is the only intent and user adds --no-plot)
    # design choice: plot and export are independent — both can run together
    if not args.export or args.save or args.ts:
        p.plot(
            value_type = args.value_type,
            bg         = args.bg,
            lims       = args.lims,
            ref_ifg    = args.ref_ifg,
            ifg_list   = args.ifg_list,
            n_x        = args.n_x,
            cbar_flag  = 1 if args.no_cbar else 0,
            textsize   = args.textsize,
            lon_rg     = args.lon_rg,
            lat_rg     = args.lat_rg,
            ts         = args.ts,
            save       = args.save,
        )


if __name__ == '__main__':
    main()
