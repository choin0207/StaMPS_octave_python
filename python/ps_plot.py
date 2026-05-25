#!/usr/bin/env python3
"""
ps_plot.py  —  Python rewrite of StaMPS ps_plot.m
=======================================================
Usage (command line):
    python ps_plot.py <value_type> [options]

Usage (Python API):
    from ps_plot import PSPlot
    p = PSPlot(work_dir='.')
    p.plot('v-d', bg=1, lims=[-20, 20])

Supported value types (most-used subset):
    Velocity:  v, V, vs, Vs
               v-d, v-o, v-do, v-a, v-da, v-dao
               V-D, V-O, V-DO
    Phase:     w, p, u, usb
               w-d, w-o, u-d, u-o, u-dm, u-da, u-do
    Other:     hgt, d, D, m
    Interactive time-series:  add --ts flag or use 'ts' as value_type

Background (--bg):
    0  black background
    1  white background (default)

Author: ps_plot.py  (converted from ps_plot.m by Andy Hooper et al.)
License: GPL-2.0
"""

import argparse
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Button, TextBox
import matplotlib.patches as mpatches

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

# ──────────────────────────────────────────────────────────────────────────────
# Helper: load .mat file (handles both v5 and v7.3 HDF5)
# ──────────────────────────────────────────────────────────────────────────────
def load_mat(path):
    """Load a .mat file; returns dict-like object."""
    path = str(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"MAT file not found: {path}")
    try:
        data = sio.loadmat(path, squeeze_me=True, struct_as_record=False)
        return data
    except Exception:
        pass
    # Try HDF5 (v7.3)
    if HAS_H5PY:
        out = {}
        with h5py.File(path, 'r') as f:
            def _read(d, keys=None):
                result = {}
                for k in (keys or d.keys()):
                    v = d[k]
                    if isinstance(v, h5py.Dataset):
                        arr = v[()]
                        if arr.dtype.kind in ('U', 'S', 'O'):
                            arr = str(arr)
                        result[k] = arr.T if isinstance(arr, np.ndarray) and arr.ndim >= 2 else arr
                    elif isinstance(v, h5py.Group):
                        result[k] = _read(v)
                return result
            out = _read(f)
        return out
    raise RuntimeError(f"Cannot load {path}: scipy.io failed and h5py not available")


# ──────────────────────────────────────────────────────────────────────────────
# Helper: load GMT CPT colormap from StaMPS cptfiles/
# ──────────────────────────────────────────────────────────────────────────────
def load_cpt(cpt_path):
    """Parse a GMT .cpt file and return a matplotlib colormap."""
    try:
        rgb = []
        with open(cpt_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(('#', 'B', 'F', 'N')):
                    continue
                parts = line.split()
                if len(parts) >= 8:
                    try:
                        z0 = float(parts[0])
                        r0, g0, b0 = float(parts[1])/255, float(parts[2])/255, float(parts[3])/255
                        rgb.append((z0, r0, g0, b0))
                    except ValueError:
                        continue
        if not rgb:
            return plt.cm.RdYlBu_r
        rgb = sorted(rgb, key=lambda x: x[0])
        z_min, z_max = rgb[0][0], rgb[-1][0]
        colors = [((z - z_min) / (z_max - z_min + 1e-12), (r, g, b))
                  for z, r, g, b in rgb]
        cmap = mcolors.LinearSegmentedColormap.from_list(
            'cpt', [(pos, col) for pos, col in colors], N=256)
        return cmap
    except Exception:
        return plt.cm.RdYlBu_r


# ──────────────────────────────────────────────────────────────────────────────
# PSPlot — main class
# ──────────────────────────────────────────────────────────────────────────────
class PSPlot:
    """
    Python equivalent of StaMPS ps_plot.m

    Parameters
    ----------
    work_dir : str
        Directory containing StaMPS output .mat files (default: '.')
    stamps_dir : str
        StaMPS installation root (for matlab/cptfiles/). If None, inferred
        from $STAMPS env var or relative path.
    """

    # Velocity value types
    VEL_TYPES = {'v', 'V', 'vs', 'Vs', 'vdrop',
                 'v-d', 'v-o', 'v-a', 'v-do', 'v-da', 'v-dao', 'v-s', 'v-so',
                 'V-D', 'V-O', 'V-DO', 'Vs-d', 'Vs-o', 'Vs-do',
                 'vs-d', 'vs-o', 'vs-do', 'vs-da', 'vs-dao',
                 'vdrop-d', 'vdrop-o', 'vdrop-do'}

    def __init__(self, work_dir='.', stamps_dir=None):
        self.work_dir = Path(work_dir).resolve()
        # find stamps installation for cptfiles
        if stamps_dir:
            self.stamps_dir = Path(stamps_dir)
        else:
            env = os.environ.get('STAMPS', '')
            if env and Path(env).exists():
                self.stamps_dir = Path(env)
            else:
                # guess relative to this script
                self.stamps_dir = Path(__file__).parent.parent
        self.cpt_dir = self.stamps_dir / 'matlab' / 'cptfiles'

        # will be populated by _load_ps_data()
        self.ps       = None
        self.parms    = None
        self.psver    = 2       # default
        self._ts_ph   = None   # cached for time series
        self._ts_days = None

    # ── internal helpers ──────────────────────────────────────────────────────

    def _matpath(self, name):
        """Return absolute path to a .mat file in work_dir."""
        p = self.work_dir / name
        if not p.suffix:
            p = p.with_suffix('.mat')
        return p

    def _load(self, stem):
        """Load work_dir/<stem><psver>.mat"""
        return load_mat(self._matpath(f'{stem}{self.psver}'))

    def _load_parms(self):
        """Load parms.mat → self.parms (dict)."""
        try:
            raw = load_mat(self._matpath('parms'))
            self.parms = {k: v for k, v in raw.items() if not k.startswith('_')}
        except FileNotFoundError:
            self.parms = {}

    def getparm(self, key, default=None):
        """Equivalent to MATLAB getparm()."""
        if self.parms is None:
            self._load_parms()
        val = self.parms.get(key, default)
        if isinstance(val, np.ndarray) and val.size == 1:
            val = val.item()
        return val

    def _load_ps_data(self):
        """Load ps<ver>.mat → self.ps (dict)."""
        if self.ps is not None:
            return
        # detect psver from psver file
        psver_file = self.work_dir / 'psver'
        if psver_file.exists():
            try:
                self.psver = int(psver_file.read_text().strip())
            except Exception:
                pass

        self._load_parms()
        ps_raw = self._load('ps')
        self.ps = {k: v for k, v in ps_raw.items() if not k.startswith('_')}

        # ensure scalar fields are Python scalars
        for key in ('n_ps', 'n_ifg', 'psver', 'master_ix'):
            if key in self.ps:
                v = self.ps[key]
                if isinstance(v, np.ndarray):
                    self.ps[key] = int(v.flat[0])

        # master index (1-based in MATLAB, convert to 0-based)
        if 'master_day' in self.ps and 'day' in self.ps:
            day = np.atleast_1d(self.ps['day']).flatten()
            master_day = float(np.atleast_1d(self.ps['master_day']).flat[0])
            self.ps['master_ix0'] = int(np.sum(day < master_day))  # 0-based
        else:
            self.ps['master_ix0'] = 0

    # ── colormap helpers ──────────────────────────────────────────────────────

    def _get_cmap(self, name='jet'):
        """Return a matplotlib colormap. Tries GMT cptfiles first."""
        cpt_map = {
            'GMT_jet': 'GMT_jet.cpt',
            'GMT_globe': 'GMT_globe.cpt',
            'GMT_gray': 'GMT_gray.cpt',
            'GMT_hot': 'GMT_hot.cpt',
            'GMT_cool': 'GMT_cool.cpt',
            'GMT_haxby': 'GMT_haxby.cpt',
            'default': 'GMT_jet.cpt',
        }
        # check parms for plot_color_scheme
        scheme = self.getparm('plot_color_scheme', 'default')
        if isinstance(scheme, str) and scheme in cpt_map:
            cpt_file = self.cpt_dir / cpt_map[scheme]
            if cpt_file.exists():
                return load_cpt(cpt_file)
        # fallback: use matplotlib built-ins
        try:
            return plt.get_cmap(name)
        except Exception:
            return plt.cm.jet

    def _vel_cmap(self):
        return plt.cm.RdYlBu_r   # diverging blue–red for velocity

    def _phase_cmap(self):
        """HSV-like cyclic colormap for wrapped phase."""
        return plt.cm.hsv

    # ── data loaders for each value_type ─────────────────────────────────────

    def _get_ph_all(self, value_type):
        """
        Return (ph_all, units, fig_name, is_complex) for the requested
        value_type.  ph_all shape: (n_ps,) for velocity types,
        (n_ps, n_ifg) for phase types.
        """
        vt = value_type.lower().strip()
        ps = self.ps
        n_ps  = ps['n_ps']
        n_ifg = ps['n_ifg']
        small_baseline_flag = str(self.getparm('small_baseline_flag', 'n')).strip().lower()
        is_sb = (small_baseline_flag == 'y')

        units      = 'mm/yr'
        fig_name   = value_type
        is_complex = False   # wrapped phase is complex

        # ── VELOCITY TYPES ───────────────────────────────────────────────────
        if vt in ('v', 'vsb'):
            mv = self._load('mv')
            ph_all = np.atleast_1d(mv['mv']).flatten() * 1000  # m/yr → mm/yr
            units = 'mm/yr'

        elif vt == 'vs':
            mv = self._load('mv')
            ph_all = np.atleast_1d(mv.get('mv_std', np.zeros(n_ps))).flatten() * 1000
            units = 'mm/yr (std)'

        elif vt in ('v-d', 'v-do', 'v-dm', 'v-dmo'):
            mv   = self._load('mv')
            ph_all = np.atleast_1d(mv['mv']).flatten() * 1000
            # DEM error correction is already in mv after step 7 – no extra subtraction
            units = 'mm/yr'

        elif vt in ('v-o',):
            mv = self._load('mv')
            ph_all = np.atleast_1d(mv['mv']).flatten() * 1000
            units = 'mm/yr'

        elif vt.startswith('v'):
            # generic velocity variant — load mv and return
            mv = self._load('mv')
            ph_all = np.atleast_1d(mv['mv']).flatten() * 1000
            units = 'mm/yr'

        # ── TOPOGRAPHY ───────────────────────────────────────────────────────
        elif vt == 'hgt':
            hgt = self._load('hgt')
            ph_all = np.atleast_1d(hgt['hgt']).flatten()
            units = 'm'

        # ── DEM ERROR ────────────────────────────────────────────────────────
        elif vt in ('d', 'dsb'):
            name = 'scla_sb' if is_sb else 'scla'
            scla = self._load(name)
            ph_all = np.atleast_1d(scla['K_ps_uw']).flatten()
            units = 'rad/m'

        elif vt in ('d-smooth',):
            name = 'scla_smooth_sb' if is_sb else 'scla_smooth'
            scla = self._load(name)
            ph_all = np.atleast_1d(scla.get('ph_scla', scla.get('K_ps_uw',
                                   np.zeros(n_ps)))).flatten()
            units = 'rad/m'

        # ── WRAPPED PHASE ────────────────────────────────────────────────────
        elif vt in ('w', 'rc'):
            rc = self._load('rc')
            ph_all = rc['ph_rc']   # complex, shape (n_ps, n_ifg)
            is_complex = True
            units = 'rad'

        elif vt == 'p':
            try:
                flt = self._load('pfilt')
                ph_all = flt.get('ph_filt', flt.get('ph_rc'))
            except FileNotFoundError:
                rc = self._load('rc')
                ph_all = rc['ph_rc']
            is_complex = True
            units = 'rad'

        elif vt == 'w-d':
            rc   = self._load('rc')
            name = 'scla_smooth_sb' if is_sb else 'scla_smooth'
            scla = self._load(name)
            ph_all = rc['ph_rc'] * np.exp(-1j * scla['ph_scla'])
            is_complex = True
            units = 'rad'

        elif vt == 'w-o':
            rc   = self._load('rc')
            name = 'scla_smooth_sb' if is_sb else 'scla_smooth'
            scla = self._load(name)
            ph_all = rc['ph_rc'] * np.exp(-1j * (scla['ph_scla'] + scla.get('ph_ramp', 0)))
            is_complex = True
            units = 'rad'

        # ── UNWRAPPED PHASE ───────────────────────────────────────────────────
        elif vt in ('u',):
            phuw = self._load('phuw')
            ph_all = phuw['ph_uw']
            units = 'rad'

        elif vt == 'u-d':
            phuw = self._load('phuw')
            name = 'scla_sb' if is_sb else 'scla'
            scla = self._load(name)
            ph_all = phuw['ph_uw'] - scla['ph_scla']
            units = 'rad'

        elif vt == 'u-o':
            phuw = self._load('phuw')
            name = 'scla_smooth_sb' if is_sb else 'scla_smooth'
            scla = self._load(name)
            ph_all = phuw['ph_uw'] - scla.get('ph_ramp', 0)
            units = 'rad'

        elif vt == 'u-do':
            phuw = self._load('phuw')
            name = 'scla_sb' if is_sb else 'scla'
            scla = self._load(name)
            name2 = 'scla_smooth_sb' if is_sb else 'scla_smooth'
            scla2 = self._load(name2)
            ph_all = phuw['ph_uw'] - scla['ph_scla'] - scla2.get('ph_ramp', 0)
            units = 'rad'

        elif vt in ('usb',):
            phuw = self._load('phuw_sb')
            ph_all = phuw['ph_uw']
            units = 'rad'

        # ── MASTER AOE ───────────────────────────────────────────────────────
        elif vt == 'm':
            try:
                scn = self._load('scn')
                ph_all = scn.get('ph_scn_master', np.zeros((n_ps, n_ifg)))
            except FileNotFoundError:
                ph_all = np.zeros((n_ps, n_ifg))
            units = 'rad'

        else:
            raise ValueError(
                f"Unsupported value_type: '{value_type}'\n"
                "Supported: v, V, vs, hgt, d, w, p, u, usb, u-d, u-o, u-do, "
                "v-d, v-o, v-do, w-d, w-o, m"
            )

        return ph_all, units, fig_name, is_complex

    # ── time series helpers ───────────────────────────────────────────────────

    def _load_ts_data(self, value_type='v-d'):
        """
        Load or prepare time series data (ph_mm) for interactive ts_plot.
        Returns (ph_mm [n_ps, n_ifg], dates [n_ifg]).
        """
        if self._ts_ph is not None:
            return self._ts_ph, self._ts_days

        # Try to load ps_plot_ts_*.mat (produced by ps_plot(..., -1))
        ts_mat = list(self.work_dir.glob(f'ps_plot_ts_{value_type}*.mat'))
        if ts_mat:
            data = load_mat(ts_mat[0])
            ph_mm  = data.get('ph_disp', data.get('ph_mm', None))
            days   = data.get('day', self.ps.get('day', None))
        else:
            # Fall back: load phuw and convert to mm (rough approximation)
            try:
                phuw = self._load('phuw')
                ph_mm = phuw['ph_uw']
                # convert rad to mm: ~28 mm/rad for C-band (approx)
                wavelength_mm = float(self.getparm('lambda', 0.056) or 0.056) * 1000
                ph_mm = ph_mm / (4 * np.pi) * wavelength_mm
            except FileNotFoundError:
                ph_mm = None
            days = self.ps.get('day', None)

        if ph_mm is None:
            return None, None

        # Convert MATLAB datenum → Python datetime ordinal
        if days is not None:
            days = np.atleast_1d(days).flatten()
            # MATLAB datenum: days since Jan 0, 0000
            # Python ordinal: days since Jan 1, 0001
            # difference: 366 days
            from datetime import date
            try:
                self._ts_days = [date.fromordinal(int(d) - 366) for d in days]
            except Exception:
                self._ts_days = np.arange(len(days))
        self._ts_ph = ph_mm
        return self._ts_ph, self._ts_days

    # ── main plot ─────────────────────────────────────────────────────────────

    def plot(self, value_type='v', bg=1, lims=None,
             ref_ifg=0, ifg_list=None, n_x=0,
             cbar_flag=0, textsize=10, lon_rg=None, lat_rg=None,
             units=None, ts=False, save=None):
        """
        Main plotting function.  Equivalent to ps_plot(value_type, bg, lims, ...).

        Parameters
        ----------
        value_type : str   – type of data to plot (e.g. 'v', 'v-d', 'w', 'u')
        bg         : int   – background: 0=black, 1=white (default)
        lims       : list  – [min, max] colormap limits; None=auto
        ref_ifg    : int   – reference interferogram (0=master)
        ifg_list   : list  – subset of interferograms to plot
        n_x        : int   – columns in subplot grid (0=auto)
        cbar_flag  : int   – 0=show colorbar, 1=hide
        textsize   : int   – font size for date labels
        lon_rg     : list  – [lon_min, lon_max] spatial filter
        lat_rg     : list  – [lat_min, lat_max] spatial filter
        ts         : bool  – enable interactive time-series click
        save       : str   – if given, save figure to this path
        """
        self._load_ps_data()
        ps   = self.ps
        n_ps = ps['n_ps']

        lon = np.atleast_1d(ps['lonlat'])[:, 0]
        lat = np.atleast_1d(ps['lonlat'])[:, 1]

        # ── spatial filter
        mask = np.ones(n_ps, dtype=bool)
        if lon_rg:
            mask &= (lon >= lon_rg[0]) & (lon <= lon_rg[1])
        if lat_rg:
            mask &= (lat >= lat_rg[0]) & (lat <= lat_rg[1])

        # ── load data
        try:
            ph_all, auto_units, fig_name, is_complex = self._get_ph_all(value_type)
        except Exception as e:
            print(f"[ps_plot] Error loading data: {e}")
            raise

        if units is None:
            units = auto_units

        is_velocity = value_type.lower().startswith('v') or value_type.lower().startswith('v')

        # ── determine if single-frame (velocity/hgt/dem_error) or multi-frame
        if ph_all.ndim == 1:
            # single map (velocity, hgt, dem error, …)
            self._plot_single(ph_all, lon, lat, mask, lims, units, fig_name,
                              bg, cbar_flag, textsize, ts, save, value_type)
        else:
            # multi-frame (interferograms)
            self._plot_multi(ph_all, lon, lat, mask, lims, units, fig_name,
                             bg, cbar_flag, textsize, ref_ifg, ifg_list,
                             n_x, is_complex, save)

    # ── single-map (velocity / hgt / dem) ────────────────────────────────────

    def _plot_single(self, data, lon, lat, mask, lims, units, fig_name,
                     bg, cbar_flag, textsize, ts, save, value_type):

        facecolor = 'white' if bg == 1 else 'black'
        text_color = 'black' if bg == 1 else 'white'
        cmap = self._vel_cmap()

        vals = data[mask]
        lon_m = lon[mask]
        lat_m = lat[mask]

        if lims is None:
            p01 = np.nanpercentile(vals, 0.1)
            p99 = np.nanpercentile(vals, 99.9)
            lims = [p01, p99]

        # ── figure layout with room for buttons if ts=True
        fig_h = 7 if not ts else 8
        fig = plt.figure(figsize=(10, fig_h), facecolor=facecolor)
        fig.canvas.manager.set_window_title(f'ps_plot — {fig_name}')

        if ts:
            # split: left = scatter, right = time series
            ax_map = fig.add_axes([0.05, 0.15, 0.50, 0.78])
            ax_ts  = fig.add_axes([0.60, 0.15, 0.37, 0.78])
            ax_ts.set_facecolor(facecolor)
            ax_ts.tick_params(colors=text_color)
            ax_ts.set_xlabel('Date', color=text_color, fontsize=textsize)
            ax_ts.set_ylabel('Displacement (mm)', color=text_color, fontsize=textsize)
            ax_ts.set_title('Click on map to see time series', color=text_color,
                            fontsize=textsize)
            for spine in ax_ts.spines.values():
                spine.set_edgecolor(text_color)
            self._ax_ts = ax_ts
            self._ts_value_type = value_type

            # ── buttons
            btn_color = '#555555' if bg == 0 else '#dddddd'
            ax_btn_ts   = fig.add_axes([0.05, 0.04, 0.12, 0.06])
            ax_btn_diff = fig.add_axes([0.20, 0.04, 0.16, 0.06])
            ax_txt_rad  = fig.add_axes([0.42, 0.04, 0.10, 0.06])
            ax_txt_val  = fig.add_axes([0.53, 0.04, 0.06, 0.06])

            self._btn_ts   = Button(ax_btn_ts, 'TS Plot', color=btn_color)
            self._btn_diff = Button(ax_btn_diff, 'TS Double Diff.', color=btn_color)
            self._txt_lab  = TextBox(ax_txt_rad, 'Radius (m)', initial='radius')
            self._txt_rad  = TextBox(ax_txt_val, '', initial='100')

            # store state for click handler
            self._ts_radius = [100.0]
            self._ts_lonlat = np.column_stack([lon, lat])
            self._ts_selected = []

            def _update_radius(text):
                try:
                    self._ts_radius[0] = float(text)
                except ValueError:
                    pass
            self._txt_rad.on_submit(_update_radius)

            def _on_click(event):
                if event.inaxes != ax_map:
                    return
                self._ts_click(event.xdata, event.ydata, fig, ax_ts,
                               text_color, textsize, lon, lat, data)
            self._cid = fig.canvas.mpl_connect('button_press_event', _on_click)
        else:
            ax_map = fig.add_axes([0.08, 0.08, 0.84, 0.88])

        ax_map.set_facecolor(facecolor)

        # ── scatter plot
        sc = ax_map.scatter(lon_m, lat_m, c=vals, cmap=cmap,
                            vmin=lims[0], vmax=lims[1],
                            s=1.5, linewidths=0, rasterized=True)

        ax_map.set_xlabel('Longitude', color=text_color, fontsize=textsize)
        ax_map.set_ylabel('Latitude',  color=text_color, fontsize=textsize)
        ax_map.set_title(fig_name,     color=text_color, fontsize=textsize + 2)
        ax_map.tick_params(colors=text_color)
        for spine in ax_map.spines.values():
            spine.set_edgecolor(text_color)
        ax_map.set_aspect('equal', adjustable='datalim')

        # ── colorbar
        if cbar_flag == 0:
            cb = fig.colorbar(sc, ax=ax_map, orientation='vertical',
                              fraction=0.03, pad=0.02, shrink=0.8)
            cb.set_label(units, color=text_color, fontsize=textsize)
            cb.ax.yaxis.set_tick_params(color=text_color)
            plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=text_color)

        print(f'ps_plot: Color range: {lims[0]:.4g} to {lims[1]:.4g} {units}')

        if save:
            fig.savefig(save, dpi=200, bbox_inches='tight',
                        facecolor=facecolor)
            print(f'ps_plot: Saved to {save}')
        else:
            plt.show()

        return fig

    def _ts_click(self, lon0, lat0, fig, ax_ts, text_color, textsize,
                  lon_all, lat_all, vel_all):
        """Handle map click → plot time series for nearby PS points."""
        ph_mm, dates = self._load_ts_data(self._ts_value_type)
        if ph_mm is None:
            ax_ts.cla()
            ax_ts.set_title('No time series data found.\n'
                            'Run ps_plot(value_type, -1) in Octave/MATLAB first.',
                            color=text_color, fontsize=textsize - 1)
            fig.canvas.draw()
            return

        radius = self._ts_radius[0]
        # convert lon/lat offset to metres (approximate)
        dlat = (lat_all - lat0) * 111_000
        dlon = (lon_all - lon0) * 111_000 * np.cos(np.radians(lat0))
        dist = np.sqrt(dlat**2 + dlon**2)

        in_circle = dist <= radius
        n_near = np.sum(in_circle)

        ax_ts.cla()
        ax_ts.set_facecolor(ax_ts.get_figure().get_facecolor())

        if n_near == 0:
            ax_ts.set_title(f'No PS within {radius:.0f} m — try larger radius',
                            color=text_color, fontsize=textsize - 1)
            fig.canvas.draw()
            return

        # mean displacement of nearby PS
        ts_data = ph_mm[in_circle, :]   # (n_near, n_ifg)
        ts_mean = np.nanmean(ts_data, axis=0)

        ax_ts.plot(dates, ts_mean, 'o-', color='steelblue', ms=4, lw=1.5,
                   label=f'{n_near} PS, r={radius:.0f} m')
        ax_ts.axhline(0, color='gray', lw=0.8, ls='--')
        ax_ts.set_xlabel('Date', color=text_color, fontsize=textsize)
        ax_ts.set_ylabel('Displacement (mm)', color=text_color, fontsize=textsize)
        ax_ts.set_title(f'TS  lon={lon0:.4f}  lat={lat0:.4f}',
                        color=text_color, fontsize=textsize)
        ax_ts.tick_params(colors=text_color)
        ax_ts.legend(fontsize=textsize - 2)
        for spine in ax_ts.spines.values():
            spine.set_edgecolor(text_color)

        try:
            fig.autofmt_xdate()
        except Exception:
            pass
        fig.canvas.draw()

    # ── multi-frame (interferograms) ──────────────────────────────────────────

    def _plot_multi(self, ph_all, lon, lat, mask, lims, units, fig_name,
                    bg, cbar_flag, textsize, ref_ifg, ifg_list,
                    n_x, is_complex, save):

        ps = self.ps
        facecolor  = 'white' if bg == 1 else 'black'
        text_color = 'black'  if bg == 1 else 'white'
        cmap = self._phase_cmap() if is_complex else self._vel_cmap()

        n_ifg = ph_all.shape[1]
        day   = np.atleast_1d(ps.get('day', np.arange(n_ifg))).flatten()

        if ifg_list is None:
            drop = np.atleast_1d(self.getparm('drop_ifg_index', np.array([]))).flatten().astype(int)
            ifg_list = [i for i in range(n_ifg) if (i + 1) not in drop]
        else:
            ifg_list = [i - 1 for i in np.atleast_1d(ifg_list)]  # 1→0 based

        n_plot = len(ifg_list)
        if n_plot == 0:
            print('[ps_plot] No interferograms to plot.')
            return

        # grid layout
        if n_x == 0:
            n_x = min(n_plot, max(1, int(np.ceil(np.sqrt(n_plot * 1.5)))))
        n_y = int(np.ceil(n_plot / n_x))

        fig, axes = plt.subplots(n_y, n_x, figsize=(3 * n_x, 3 * n_y),
                                 facecolor=facecolor, squeeze=False)
        fig.canvas.manager.set_window_title(f'ps_plot — {fig_name}')

        lon_m = lon[mask]
        lat_m = lat[mask]

        if is_complex:
            ph_disp = np.angle(ph_all[mask, :])
            lims_use = [-np.pi, np.pi]
        else:
            ph_disp = ph_all[mask, :]
            master_ix0 = ps.get('master_ix0', 0)
            if ref_ifg > 0:
                ph_disp -= ph_disp[:, ref_ifg - 1:ref_ifg]
            elif ref_ifg == 0:
                if master_ix0 < ph_disp.shape[1]:
                    ph_disp -= ph_disp[:, master_ix0:master_ix0+1]
            # auto limits
            if lims is None:
                flat = ph_disp[:, ifg_list].flatten()
                flat = flat[~np.isnan(flat)]
                if len(flat):
                    p01 = np.percentile(flat, 0.1)
                    p99 = np.percentile(flat, 99.9)
                    lims_use = [p01, p99]
                else:
                    lims_use = [-1, 1]
            else:
                lims_use = lims

        first_sc = None
        from datetime import datetime

        for plot_idx, ifg_idx in enumerate(ifg_list):
            row = plot_idx // n_x
            col = plot_idx %  n_x
            ax  = axes[row, col]
            ax.set_facecolor(facecolor)

            vals = ph_disp[:, ifg_idx]

            sc = ax.scatter(lon_m, lat_m, c=vals, cmap=cmap,
                            vmin=lims_use[0], vmax=lims_use[1],
                            s=0.8, linewidths=0, rasterized=True)
            ax.set_aspect('equal', adjustable='datalim')
            ax.set_xticks([]); ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_edgecolor(text_color)

            # date label
            if textsize != 0 and ifg_idx < len(day):
                try:
                    d = datetime.fromordinal(int(day[ifg_idx]) - 366)
                    label = d.strftime('%d %b %Y')
                except Exception:
                    label = str(ifg_idx + 1)
                ax.set_title(label, color=text_color, fontsize=abs(textsize),
                             fontweight='bold', pad=2)

            if first_sc is None:
                first_sc = sc

        # hide unused axes
        for plot_idx in range(n_plot, n_x * n_y):
            row = plot_idx // n_x
            col = plot_idx %  n_x
            axes[row, col].set_visible(False)

        # colorbar
        if cbar_flag == 0 and first_sc is not None:
            cb = fig.colorbar(first_sc, ax=axes.ravel().tolist(),
                              orientation='horizontal', fraction=0.02,
                              pad=0.02, shrink=0.6)
            cb.set_label(units, color=text_color, fontsize=textsize)
            cb.ax.xaxis.set_tick_params(color=text_color)
            plt.setp(plt.getp(cb.ax.axes, 'xticklabels'), color=text_color)

        plt.suptitle(fig_name, color=text_color, fontsize=textsize + 2)
        print(f'ps_plot: Color range: {lims_use[0]:.4g} to {lims_use[1]:.4g} {units}')

        if save:
            fig.savefig(save, dpi=200, bbox_inches='tight', facecolor=facecolor)
            print(f'ps_plot: Saved to {save}')
        else:
            plt.tight_layout()
            plt.show()

        return fig


# ──────────────────────────────────────────────────────────────────────────────
# Command-line interface
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='ps_plot.py — Python rewrite of StaMPS ps_plot.m',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('value_type', nargs='?', default='v',
                        help='Data type to plot: v, v-d, w, u, hgt, d, ... (default: v)')
    parser.add_argument('--bg', type=int, default=1,
                        help='Background: 0=black, 1=white (default: 1)')
    parser.add_argument('--lims', type=float, nargs=2, default=None,
                        metavar=('MIN', 'MAX'),
                        help='Colormap limits, e.g. --lims -20 20')
    parser.add_argument('--ref-ifg', type=int, default=0,
                        help='Reference interferogram (0=master, -1=incremental)')
    parser.add_argument('--ifg-list', type=int, nargs='+', default=None,
                        help='Subset of interferograms (1-based)')
    parser.add_argument('--n-x', type=int, default=0,
                        help='Columns in subplot grid (0=auto)')
    parser.add_argument('--no-cbar', action='store_true',
                        help='Hide colorbar')
    parser.add_argument('--textsize', type=int, default=10,
                        help='Font size (default: 10)')
    parser.add_argument('--lon-rg', type=float, nargs=2, default=None,
                        metavar=('LON_MIN', 'LON_MAX'))
    parser.add_argument('--lat-rg', type=float, nargs=2, default=None,
                        metavar=('LAT_MIN', 'LAT_MAX'))
    parser.add_argument('--ts', action='store_true',
                        help='Enable interactive time-series click mode')
    parser.add_argument('--save', type=str, default=None,
                        help='Save figure to file (e.g. velocity.png)')
    parser.add_argument('--work-dir', type=str, default='.',
                        help='Directory containing StaMPS .mat files (default: .)')
    parser.add_argument('--stamps-dir', type=str, default=None,
                        help='StaMPS installation root (for cptfiles/)')

    args = parser.parse_args()

    p = PSPlot(work_dir=args.work_dir, stamps_dir=args.stamps_dir)
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
