#-------------------------------------------------------------------------------------
# Calculate the target curve from the equal loudness contour and slope.
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
from scipy.interpolate import interp1d

from Math import linear_interpolation, apply_curve, calc_slope_curve
from Utils import read_fr_data, read_eq_data, read_eloud_fr_data, read_spkr_fr_data


# Functions that shave the low and high of the target curve.
def low_and_high_shave_off(f_range, gains):
    """
    Functions that shave the low and high of the target curve.
    Notis: There is no particular rationale for this.
    
    Args:
    - gains (array): array of gains of curve.
    - f_range (ndarray):  NumPy ndarray of frequencies.
    
    Returns:
    - target_curve (ndarray): NumPy ndarray of target curve.
    """
    
    a_low = [-30, 3.6, 1.5, 0.2]
    a_hi  = [-2, 6, 1.5, 5]
    
    target_curve = gains + a_low[0]*(a_low[2]/np.log10(f_range) - a_low[3])**a_low[1]  + a_hi[0]*(a_hi[2]/(np.log10(f_range) - a_hi[3]))**a_hi[1]
    
    return target_curve

# Calculation of the ear canal transfer function
def ear_canal_transfer_function(f_range):
    """
    Functions that shave the low and high of the target curve.
    Ref: Enamito, Hiruma (2012) Transactions of the Japan Society of Mechanical Engineers (Volume B), Vol.78, Issue 789, pages 979
    
    Args:
    - f_range (ndarray):  NumPy ndarray of frequencies.
    
    Returns:
    - (ndarray): NumPy ndarray of ear_canal_transfer_function curve.
    """
    
    ro = 1.293       #Air density [kg/m3]
    D4 = 0.007       #Diameter of ear canal [m].
    S4 = D4**2*np.pi #Cross-sectional area of ear canal [m2].
    L4 = 0.0255       #Length of ear canal [m].
    c  = 352.28      #Speed of sound in ear canal [m/sec].
    Zd = np.sqrt(10)*ro*c #tympanic impedance
    x  = L4 #Measurement position
    
    ks  = 2 * np.pi * f_range / c #wavenumber
    
    A = Zd*np.cos(ks*(L4 - x)) + 1j*ro*c*np.sin(ks*(L4 - x))
    B = Zd*np.cos(ks*L4) + 1j*ro*c*np.sin(ks*L4)
    
    H_open = A/B
    
    return 6*np.log2(np.abs(H_open))    

# Plot the curves---------------------------------------------------------------
def plot_eq_curve(data, output_folder):
    
    # plot setting
    plt.figure(figsize=(8, 6))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain (dB)')
    plt.title('Target Frequency Response Data')
    plt.xscale('log')
    plt.grid(True)
    plt.xlim(20, 20000)
    plt.ylim(-20, 20)
    plt.minorticks_on()
    plt.grid(which="major", color="black", alpha=0.5)
    plt.grid(which="minor", color="gray", alpha=0.1)

    # Plotting Data
    plt.plot(data[:, 0], data[:, 1], label='HRTF', color='lightblue')
    plt.plot(data[:, 0], data[:, 2], label='ECTF', color='limegreen')
    plt.plot(data[:, 0], data[:, 3], label='HRTF - ECTF', color='steelblue')
    plt.plot(data[:, 0], data[:, 4], label='Org Target', color='pink')
    plt.plot(data[:, 0], data[:, 5], label='Target', color='tomato')


    # Show legend
    plt.legend()

    # Saving Graphs
    plt.savefig('target_FR_data_plot.png')

    # Graph Display
    plt.close()
    
    # Move and overwrite files
    os.replace("plot_artificial_flat_target.png", output_folder.joinpath("plot_natural_flat_target.png"))
    
# main----------------------------------------------------------------------------------
def target_calc(eloud_file_path, output_folder, slope, hrtf_path):
    
    f_range = np.logspace(np.log10(20), np.log10(20000), 1000)
    
    fq_elouds, g_elouds = read_eloud_fr_data(eloud_file_path)

    interpolator_eloud = interp1d(fq_elouds, g_elouds, kind='linear', fill_value="extrapolate")
    eloud_curve = interpolator_eloud(f_range)
    
    slope_curve = calc_slope_curve(f_range, slope)
    
    target_curve = -apply_curve(eloud_curve, slope_curve)
    
    target_curve = low_and_high_shave_off(f_range, target_curve) #Low and high shaved off
    
    gain_tmp = linear_interpolation(f_range, target_curve, 1000)
    target_curve_std = target_curve - gain_tmp
    
    #Head transfer function - External auditory canal transfer function
    if os.path.isfile(hrtf_path):
        df_hrtf = read_fr_data(hrtf_path)
        interpolator = interp1d(np.log10(df_hrtf['freq']), df_hrtf['gain'], kind='linear', fill_value="extrapolate")
        hrtf_curve = interpolator(np.log10(f_range))
        ectf_curve = ear_canal_transfer_function(f_range)
        target_curve_std2 = target_curve_std + hrtf_curve - ectf_curve
        data = np.column_stack((f_range, hrtf_curve, ectf_curve, hrtf_curve - ectf_curve, target_curve_std, target_curve_std2))
        np.savetxt(output_folder.resolve().joinpath("target_curve_natural_flat.txt"), data[:,[0,5]], delimiter=',', fmt='%.6f')
        plot_eq_curve(data, output_folder)
    else:
        data = np.column_stack((f_range, target_curve_std))
        np.savetxt(output_folder.resolve().joinpath("target_curve_natural_flat.txt"), data[:,[0,1]], delimiter=',', fmt='%.6f')