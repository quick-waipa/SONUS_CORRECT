import pandas as pd
import numpy as np

def linear_interpolation(f_range, gains, target_freq):
    """
    Find the two frequencies in f_range that are closest to target_freq.
    
    Args:
    - f_range (ndarray):  NumPy ndarray of frequencies.
    - gains (array): array of gains.
    - target_freq (float): target frequency.
    
    Returns:
    - interpolated_gain (float): interpolated gain of target_freq.
    """
    
    idx = 0
    while idx < len(f_range) - 1 and f_range[idx + 1] < target_freq:
        idx += 1
    
    # linear interpolation
    if idx == len(f_range) - 1:  # For the last element
        interpolated_gain = gains[idx]
    else:
        # Get two frequencies and the corresponding GAIN
        freq_lower, freq_upper = f_range[idx], f_range[idx + 1]
        gain_lower, gain_upper = gains[idx], gains[idx + 1]
        
        # linear interpolation
        interpolated_gain = gain_lower + (gain_upper - gain_lower) * ((target_freq - freq_lower) / (freq_upper - freq_lower))
    
    return interpolated_gain

def gaussian_function(x, a, b, c):
    """
    Gaussian function for modeling peaks.
    
    Args:
    - x (array): Input data.
    - a (float): Amplitude.
    - b (float): Center frequency.
    - c (float): Standard deviation.
    
    Returns:
    - array: Gaussian function values.
    """
    
    return a * np.exp(-(x - b)**2 / (2 * c**2))

# apply curve--------------------------------------------------------
def apply_curve(curve_a, curve_b):
    """
    Sum the two frequency response curves together.
    
    Args:
    - curve_a (ndarray):  NumPy ndarray of FR data.
    - curve_b (ndarray):  NumPy ndarray of FR data.
    
    Returns:
    - curve (ndarray): NumPy ndarray of summed FR curve.
    """
    
    curve = curve_a + curve_b
    
    return curve

# calc slope--------------------------------------------------------
def calc_slope_curve(f_range, slope):
    """
    Calculate the slope curve from slope [dB/oct].
    
    Args:
    - f_range (ndarray):  NumPy ndarray of frequencies.
    - slope (float): slope [dB/oct].
    
    Returns:
    - slope_curve (ndarray): NumPy ndarray of slope curve.
    """
    
    fr0 = np.log2(1000)
    
    slope_curve = slope*(np.log2(f_range) - fr0)
    
    return slope_curve

# calculate peak filter--------------------------------------------------------
def calculate_peak_filter(f0, gain, q_factor, f_range):
    """
    Calculate the EQ curve from frequency, gain, and Q factor.
    
    Args:
    - f0 (float): peak frequency.
    - gain (float): peak gain.
    - q_factor (float): peak Q factors.
    - f_range (ndarray):  NumPy ndarray of frequencies.
    
    Returns:
    - output (ndarray): NumPy ndarray of EQ curve(peak filter).
    """
    
    w0 = 2 * np.pi * f0 / f_range
    w  = 2 * np.pi * 1
    jw = np.zeros(len(f_range)) + 1j * w
    g  = 2**(gain/6)
    
    b0 = w0**2 + 1j * np.zeros(len(f_range))
    b1 = g*(w0/q_factor) + 1j * np.zeros(len(f_range))
    b2 = np.full(len(f_range), 1) + 1j * np.zeros(len(f_range))
    a0 = w0**2 + 1j * np.zeros(len(f_range))
    a1 = 1/g*w0/q_factor + 1j * np.zeros(len(f_range))
    a2 = np.full(len(f_range), 1) + 1j * np.zeros(len(f_range))
        
    H = (b0 + b1 * jw + b2 * jw**2) / (a0 + a1 * jw + a2 * jw**2)
    
    output = np.abs(H)

    return output

def calculate_eq_curve(f0s, gains, q_factors, f_range):
    """
    Calculate the EQ curve from peak filters.
    
    Args:
    - f0s (array): array of frequencies of peak filters.
    - gains (array): array of gains of peak filters.
    - q_factors (array): array of Q factors of peak filters.
    - f_range (ndarray):  NumPy ndarray of frequencies.
    
    Returns:
    - eq_curve (ndarray): NumPy ndarray of EQ-curve.
    """
    
    eq_curve = np.full(len(f_range), 0.0)
    Ptotal = np.full(len(f_range), 0.775)
    for freq, gain, q in zip(f0s, gains, q_factors):
        Pi = Ptotal*calculate_peak_filter(freq, gain, q, f_range)
        Gi = 3*np.log2(Pi/0.775)
        eq_curve += Gi
    return eq_curve