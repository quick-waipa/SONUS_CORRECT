#-------------------------------------------------------------------------------------
# Program to generate eqfilter for sound field correction from frequency response data
#-------------------------------------------------------------------------------------

import os
import subprocess
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.signal import find_peaks

from Math import linear_interpolation, gaussian_function, apply_curve, calculate_eq_curve
from Utils import read_fr_data, remove_duplicates


def interpolate_gain(df, target_freq):
    """
    Interpolate gain at the target frequency using neighboring frequencies.
    
    Args:
    - df (DataFrame): Dataframe containing frequency and gain columns.
    - target_freq (float): Target frequency for interpolation.
    
    Returns:
    - float: Interpolated gain at the target frequency.
    """
    
    # Find the neighboring frequencies
    freqs = df['freq'].values
    gains = df['gain'].values
    idx = np.argsort(abs(freqs - target_freq))
    nearest_freqs = freqs[idx[:2]]
    nearest_gains = gains[idx[:2]]
    
    # Perform linear interpolation
    interpolated_gain = np.interp(target_freq, nearest_freqs, nearest_gains)
    return interpolated_gain

def find_dips(df, low_cutoff, high_cutoff):
    """
    Find dips in frequency response data and output them.
    
    Args:
    - df (DataFrame): Dataframe containing frequency and gain columns.
    - low_cutoff (float): Low cutoff frequency.
    - High_cutoff (float): High cutoff frequency.
    
    Returns:
    - dips (array): Freauencies of dips.
    - dip_gains (array): Gains of dips.
    - q_factors (array): Q factors of dips.
    """
    
    filtered_df = df[(df['freq'] >= low_cutoff) & (df['freq'] <= high_cutoff)]
    
    freqs = filtered_df['freq'].to_numpy()
    gains = filtered_df['gain'].to_numpy()
    gains_inverted = -gains
    
    # Find the moving average
    window_size = int(len(freqs)/3)
    smoothed_gains = np.convolve(gains_inverted, np.ones(window_size)/window_size, mode='same')

    # Subtract moving average from frequency response
    adjusted_gains = gains_inverted[:len(smoothed_gains)] - smoothed_gains
    
    std_gains = adjusted_gains / adjusted_gains.max()
    
    peaks, _ = find_peaks(std_gains, height=0.3)
    
    # Calculate the distance between peaks and exclude peaks that are close together
    min_peak_distance = 0.5  # Minimum peak-to-peak spacing [oct].
    filtered_peaks = [peaks[0]]  # Always leave the first peak
    for i in range(1, len(peaks)):
        if np.log2(freqs[peaks[i]]) - np.log2(freqs[peaks[i-1]]) >= min_peak_distance:
            filtered_peaks.append(peaks[i])
        if gains[peaks[i]] < gains[peaks[i-1]]:
            filtered_peaks.pop(len(filtered_peaks) - 1)
            filtered_peaks.append(peaks[i])
    
    dip_gains = gains[filtered_peaks]
    dips = freqs[filtered_peaks]
    #dip_gains = dip_gains / dip_gains.max()
    print("dips[Hz]: ",dips)
    
    q_factors = []
    
    for i in range(len(dips)):
        q_factor = estimate_q_factor(filtered_df, dips[i], dip_gains[i], 0.1, 8, 1, 4)
        q_factors.append(q_factor + 2)    
    
    return dips, dip_gains, q_factors


def find_peak_and_dip(df, df_t):
    """
    Find the peak and dip from the data.
    
    Args:
    - df (DataFrame): Dataframe containing frequency and gain columns.
    - df_t (DataFrame): Dataframe containing frequency and gain columns.
    
    Returns:
    - float: Frequency of the peak or dip.
    - float: Gain at the peak or dip frequency.
    """
    
    df_t_tmp = df_t.rename(columns={'gain':'gain_t'})
    merged_df = pd.merge(df, df_t_tmp, on='freq')
    merged_df['gain'] = merged_df['gain'] - merged_df['gain_t']
    df_r = merged_df[['freq','gain']]
    
    # Find the maximum and minimum gain
    max_g = df_r['gain'].max()
    min_g = df_r['gain'].min()
    
    # Check which one is further from the target gain
    max_g_freq = df_r[df_r['gain'] == max_g]['freq'].values[0]
    min_g_freq = df_r[df_r['gain'] == min_g]['freq'].values[0]
    
    
    if abs(max_g) > abs(min_g): #If the peak is the target
        # Peak is further from the target gain
        return max_g_freq, df.loc[df['freq'] == max_g_freq, 'gain'].values[0]
    else: #If the dip is the target
        # Dip is further from the target gain
        return min_g_freq, df.loc[df['freq'] == min_g_freq, 'gain'].values[0]
    
def estimate_neighbor_freq(df_filtered, freq, gain, window_oct):
    """
    Estimate the neighbor frequency using Gaussian peak modeling.
    
    Args:
    - df_filtered (DataFrame): Filtered data.
    - freq (float): Frequency of the peak or dip.
    - gain (float): Gain at the peak or dip frequency.
    
    Returns:
    - float: Estimated neighbor frequency.
    """
    
    # Get frequencies and gains from the filtered dataframe
    freqs = df_filtered['freq'].values
    gains = df_filtered['gain'].values
    
    # Extract data within the window around the peak frequency
    f_hi = 2**(np.log2(freq) + window_oct)
    f_lo = 2**(np.log2(freq) - window_oct)
    idx = (freqs >= f_lo) & (freqs <= f_hi)
    freqs_window = np.log10(freqs[idx])
    gains_window = gains[idx]
    
    # Fit Gaussian function to the data
    sigma = 1/(np.sqrt(2*np.pi)*gain)
    gamma = 1
    p0  = [gain, np.log10(freq), sigma]  # Initial guess for the parameters
    pv0 = [gain, np.log10(freq), sigma, gamma]
    
    try:
        params, _ = curve_fit(gaussian_function, freqs_window, gains_window, p0=p0)
    except RuntimeError:
        print("---Gaussian Curve fitting failed.---")
        amplitude = gain
        
        #try:
        #    params, _ = curve_fit(voigt_function, freqs_window, gains_window, p0=pv0)
        #except RuntimeError:
        #    print("---Voigt Curve fitting failed.---")
        #else:
        #    print("---Complete Voigt fitting---")
        #    amplitude, center_freq, std_dev = params
    except TypeError as e:
        print("---Gaussian Curve fitting Error---")
        amplitude = gain
    else:
        print("---Complete Gaussian fitting---")
        # Get the parameters of the Gaussian function
        amplitude, center_freq, std_dev = params
    
    # Estimate neighbor frequency as the frequency at -3 dB from the peak
    neighbor_freq = freq * 10**((gain - 3) / (20 * amplitude))
    
    return neighbor_freq
    
def estimate_q_factor(df_filtered, freq, gain, window_oct, max_q, min_q, default_q):
    """
    Estimate Q factor.
    
    Args:
    - df_filtered (DataFrame): Filtered data.
    - freq (float): Frequency of the peak or dip.
    - gain (float): Gain at the peak or dip frequency.
    
    Returns:
    - float: Estimate Q factor.
    """
        
    # Find the neighboring frequencies closest to 3 dB below the peak/dip gain
    freqs = df_filtered['freq'].values
    gains = df_filtered['gain'].values
    neighbor_freq = estimate_neighbor_freq(df_filtered, freq, gain, window_oct)
    
    # Check if neighbor_freq is assigned before using it
    if neighbor_freq is None:
        print("Neighbor frequency not found.")
        return None
    
    # Check if neighbor_freq is lower than the peak/dip frequency
    if neighbor_freq < freq:
        print("Neighbor frequency is lower than the peak/dip frequency.")
        q_factor = default_q
        return q_factor
    
    # Calculate the Q factor
    mfreq = 10**(np.log10(freq) - (np.log10(neighbor_freq) - np.log10(freq)))
    oct = np.log2(neighbor_freq / mfreq)
    q_factor = 1.41 / oct
    if q_factor > max_q:
        q_factor = max_q
    elif q_factor < min_q:
        q_factor = min_q
        
    return q_factor

def plot_data_and_curve(freqs, gains0, gains, eq_curve, t_curve, out, output_folder):

    data = np.column_stack((freqs, gains0))
    eqd_data = np.column_stack((freqs, gains))
    eq_curve = np.column_stack((freqs, eq_curve))
    t_curve = np.column_stack((freqs, t_curve))

    # plot setting
    plt.figure(figsize=(8, 6))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain (dB)')
    plt.title('Equalization Curve')
    plt.xscale('log')
    plt.grid(True)
    plt.xlim(20, 20000)
    plt.ylim(-20, 20)
    plt.minorticks_on()
    plt.grid(which="major", color="black", alpha=0.5)
    plt.grid(which="minor", color="gray", alpha=0.1)

    # Plotting Data
    plt.plot(t_curve[:, 0], t_curve[:, 1], '--', label='Target Curve', color='tomato')
    plt.plot(data[:, 0], data[:, 1], label='Frequency Respons', color='lightblue', linewidth=2)
    plt.plot(eq_curve[:, 0], eq_curve[:, 1], label='EQ Curve', color='deeppink', linewidth=1)
    plt.plot(eqd_data[:, 0], eqd_data[:, 1], label='EQd Frequency Respons', color='steelblue', linewidth=2)

    # Show legend
    plt.legend()

    # Saving Graphs
    plt.savefig('flat_target.png')

    # Graph Display
    plt.close()
    
    os.rename("flat_target.png" ,out + "flat_target.png" )
    
    # Move and overwrite files
    os.replace(out + "flat_target.png", output_folder.joinpath(out + "flat_target.png"))
    
    
def write_eq_settings(fs, gs, qs, out_path, model_str):
    
    current_datetime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    with open(out_path, 'w') as file:
        for i in range(len(fs)):
            freq = fs[i]
            gain = gs[i]
            q    = qs[i]
            n    = i + 1
            file.write(f"Filter {n}: ON  PK  Fc  {freq:.2f} Hz  Gain  {gain:.2f} dB  Q  {q:.3f}\n")    


def eq_make(data):
    
    #INPUT================================================================

    band_num = data['band_num'] 

    file_path = data['file_path'] 
    out_path  = data['out_path'] #eq filter
    model_str = data['model_str'] 

    max_q     = data['max_q'] 
    min_q     = data['min_q'] 
    default_q = data['default_q'] 

    window_oct = data['window_oct'] 
    
    low_cutoff = data['low_cutoff'] 
    high_cutoff = data['high_cutoff'] 

    target = data['target'] 
    target_path = data['target_path']
    
    out = data['out']
    output_folder = data['output_folder']
    
    target_on = data['target_on']
    
    dip_alpha = data['dip_alpha']
    
    #hrtf_path = data['hrtf_path']

    #=======================================================================
    
    # Load data
    df   = read_fr_data(file_path)
    
    # Remove duplicates
    df_no_duplicates = remove_duplicates(df)
    
    df_curve = df_no_duplicates
    
    #Standardized at 1000Hz gain
    gain_tmp = linear_interpolation(df_curve['freq'].to_numpy(), df_curve['gain'].to_numpy(), 1000)
    df_curve.loc[:, 'gain'] -= gain_tmp
    
    freqs  = df_curve['freq']
    gains0 = df_curve['gain']
    gains  = df_curve['gain']
    
    dip_freqs, dip_gains, dip_qs = find_dips(df_curve, low_cutoff, high_cutoff)
    
    if target_on:
        df_t = read_fr_data(target_path)
        interpolator = interp1d(np.log10(df_t['freq']), df_t['gain'], kind='linear', fill_value="extrapolate")
        t_curve = interpolator(np.log10(freqs))
        t_curve = t_curve + target
    else:
        t_curve = np.zeros_like(freqs) + target
        
    for dip_freq in dip_freqs:
        dip_gains[dip_freqs == dip_freq] -= t_curve[freqs == dip_freq]
    
    eq_dips = calculate_eq_curve(dip_freqs, dip_gains, dip_qs, freqs)*(1 - dip_alpha)
    t_curve_dips = apply_curve(t_curve, eq_dips)
    
    df_t_curve = pd.DataFrame({'freq':freqs, 'gain':t_curve_dips})
    
    q_factors = []
    f0s = []
    eq_gains = [] 
    
    print("===========================================================================")
    print("Generate EQ curve")
    print("Load FR Data:   ", file_path)
    print("Output EQ Data: ", out_path)
    print("===========================================================================")
    
    for i in range(0,band_num,1):
        
        print("band num: ", i + 1)
        
        gains = df_curve['gain']
        
        # Filter the data around the peak or dip frequency
        df_filtered = df_curve[(df_curve['freq'] >= low_cutoff) & (df_curve['freq'] <= high_cutoff)]
        
        # Find the peak or dip
        target_freq, target_gain = find_peak_and_dip(df_filtered, df_t_curve)
        
        print(f"Target frequency: {target_freq} Hz")
        print(f"Target gain: {target_gain} dB")
        # Estimate the Q factor
        q_factor = estimate_q_factor(df_curve, target_freq, target_gain, window_oct, max_q, min_q, default_q)
        
        print(f"Estimated Q factor: {q_factor}")
        
        q_factors.append(q_factor)
        f0s.append(target_freq)
        
        eq_gains.append(-target_gain + df_t_curve.loc[df_t_curve['freq'] == target_freq, 'gain'].values[0])

        # make equalizer
        eq_curve = calculate_eq_curve(f0s, eq_gains, q_factors, freqs)
        
        # apply equalizer
        eqd_curve = apply_curve(gains0, eq_curve)
        
        df_curve = pd.DataFrame({'freq':freqs, "gain":eqd_curve})
        
        print("---------------------------------------")
    
    # write eq settings
    write_eq_settings(f0s, eq_gains, q_factors, out_path, model_str)
    
    gains = df_curve['gain']
    
    # Plot data and fitting curve
    plot_data_and_curve(freqs, gains0, gains, eq_curve, t_curve_dips ,out, output_folder)
    