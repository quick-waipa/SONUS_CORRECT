#-------------------------------------------------------------------------------------
# Calculate the Frequency Response Integral:FRI value and diff from the frequency response curve.
#-------------------------------------------------------------------------------------

import os
import shutil
import numpy as np
import pandas as pd
import re
import subprocess
import matplotlib.pyplot as plt
import cmath
from pathlib import Path
from scipy.integrate import simpson
from scipy.interpolate import interp1d

from Math import linear_interpolation, apply_curve, calc_slope_curve, calculate_eq_curve
from Utils import read_fr_data, read_eq_data, read_eloud_fr_data, read_spkr_fr_data

# calcurate fri -----------------------------------------------------------------------
def calc_fri(curve, f_range):
    """
    Calculate the Frequency Response Integral:FRI value from the frequency response curve.
    
    Args:
    - curve (ndarray):  NumPy ndarray of gains.
    - f_range (ndarray):  NumPy ndarray of frequencies.
    
    Returns:
    - fri (float): Frequency Response Integral:FRI value.
    """
    
    curve = 0.775*2**(curve/6)
    
    x = np.log10(f_range)
    
    fri = simpson(curve, x) / (np.log10(20000) - np.log10(20))
    
    fri = 6*np.log2(fri/0.775)
    
    return fri
    
# main----------------------------------------------------------------------------------
def fri_calc(eq_path, spkr_path, eloud_path, slope):
    """
    Calculate the Frequency Response Integral:FRI value and diff.
    
    Args:
    - eq_path:  eq curve file path.
    - spkr_path:  spkr FR curve file path.
    - eloud_path:  Equal Loudness curve file path.
    - slope (float):  slope [dB/oct].
    
    Returns:
    - fri_org (float): Frequency Response Integral:FRI value of Original Speaker FR curve.
    - fri_eqd (float): Frequency Response Integral:FRI value of EQd Speaker FR curve.
    - fri_diff (float): diff
    """
    
    f_range = np.logspace(np.log10(20), np.log10(20000), 1000)
    
    fq_eqs, g_eqs, qs   = read_eq_data(eq_path)
    fq_elouds, g_elouds = read_eloud_fr_data(eloud_path)
    fq_spkrs, g_spkrs   = read_spkr_fr_data(spkr_path)

    interpolator = interp1d(fq_spkrs, g_spkrs, kind='linear', fill_value="extrapolate")
    spkr_curve = interpolator(f_range)
    
    eq_curve = calculate_eq_curve(fq_eqs, g_eqs, qs, f_range)
    
    interpolator = interp1d(fq_elouds, g_elouds, kind='linear', fill_value="extrapolate")
    eloud_curve = interpolator(f_range)
    
    slope_curve = calc_slope_curve(f_range, slope)
    
    filter_curve = apply_curve(eloud_curve, slope_curve)
    
    filtered_spkr_curve = apply_curve(filter_curve, spkr_curve)
    
    eqd_spkr_curve = apply_curve(eq_curve, filtered_spkr_curve)

    fri_org = calc_fri(filtered_spkr_curve, f_range)
    
    fri_eqd = calc_fri(eqd_spkr_curve, f_range)
    
    fri_diff = fri_org - fri_eqd
    
    return fri_org, fri_eqd, fri_diff