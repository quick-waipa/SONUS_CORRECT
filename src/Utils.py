import pandas as pd
import numpy as np
import re

def read_fr_data(file_path):
    """
    Load frequency data from a text file.
    
    Args:
    - file_path (str): Path to the text file.
    
    Returns:
    - DataFrame: Loaded data.
    """
    df = pd.read_csv(file_path, header=None, names=['freq', 'gain'])
    return df

# file read and setting--------------------------------------------------------------
def read_eq_data(file_path):
    frequencies = []
    gains = []
    q_factors = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('Filter'):
                if line.split()[2] == "ON":
                    freq = float(line.split()[5])
                    gain = float(line.split()[8])
                    q = float(line.split()[11])
                    frequencies.append(freq)
                    gains.append(gain)
                    q_factors.append(q)
                    #print("freq: ",freq," gain: ",gain," q: ",q)
    return frequencies, gains, q_factors

# k-file read and setting--------------------------------------------------------------
def read_eloud_fr_data(file_path):
    frequencies = []
    gains = []
    with open(file_path, 'r') as file:
        for line in file:
            freq = float(re.split(r'[, \t]+', line)[0])
            gain = float(re.split(r'[, \t]+', line)[1])
            frequencies.append(freq)
            gains.append(gain)
            #print("freq: ",freq," gain: ",gain)
    return frequencies, gains

# msp3 data read and setting--------------------------------------------------------------
def read_spkr_fr_data(file_path):
    frequencies = []
    gains = []
    with open(file_path, 'r') as file:
        i = 0
        for line in file:
            freq = float(re.split(r'[, \t]+', line)[0])
            gain = float(re.split(r'[, \t]+', line)[1])
            if len(frequencies) != 0:
                freq_pre = frequencies[len(frequencies) - 1]
            else:
                freq_pre = 0
                
            if freq_pre != freq:
                frequencies.append(freq)
                gains.append(gain)
            i += 1
            #print("freq: ",freq," gain: ",gain)
    return frequencies, gains

# read from FRI file--------------------------------------------------------------
def read_fri_diff(file_path):
    i = 0
    diff = []
    with open(file_path, 'r') as file:
        for line in file:
            if i == 7 or i == 13:
                diff = float(re.split(r'[, \t]+', line)[2])
            i += 1
    return diff


def remove_duplicates(df):
    """
    Remove duplicate rows from the dataframe.
    
    Args:
    - df (DataFrame): Dataframe containing frequency and gain columns.
    
    Returns:
    - DataFrame: Dataframe with duplicate rows removed.
    """
    df_no_duplicates = df.drop_duplicates()
    return df_no_duplicates

def write_eq_settings_yml0(out_path, target_type):
    
    if target_type == "artificial":
        with open(out_path, 'w') as file:
            file.write(f"devices:\n" +
                       f"  capture:\n" +
                       f"    type: CoreAudio\n" +
                       f"    device: \"BlackHole 2ch\"\n" +
                       f"  playback:\n" +
                       f"    type: CoreAudio\n" +
                       f"    device: \"MacBook Pro Speakers\"\n" +
                       f"\n" +
                       f"filters:\n")
            

def write_eq_settings_yml1(fs, gs, qs, out_path, target_type):
            
    with open(out_path, 'a') as file:
        for i in range(len(fs)):
            freq = fs[i]
            gain = gs[i]
            q    = qs[i]
            n    = i + 1
            title= target_type + "_eq" + str(n)
            file.write(f"  {title}:\n" +
                       f"    type: Biquad\n" +
                       f"    parameters:\n" +
                       f"      type: Peaking\n" +
                       f"      freq: {freq:.2f}\n" +
                       f"      q: {q:.3f}\n" +
                       f"      gain: {gain:.2f}\n")

def write_eq_settings_yml2(out_path, target_type, g_diff):
            
    with open(out_path, 'a') as file:
        title= target_type + "_gain"   
        file.write(f"  {title}:\n" +
                   f"    type: Gain\n" +
                   f"    parameters:\n" +
                   f"      gain: {g_diff}\n")

def write_eq_settings_yml3(out_path, lr, band_num):
            
    with open(out_path, 'a') as file:
        file.write(f"\n" +
                   f"pipeline:\n")

        if lr == "L":
            ch = [2,4]
        else:
            ch = [3,5]
            
        for j in ch:
            file.write(f"  - type: Filter\n" +
                       f"    channel: {j}\n"
                       f"    names:\n")
            for k in range(band_num):
                n = k + 1
                if j == 2 or j == 3:
                    title= "artificial" + "_eq" + str(n)
                else:
                    title= "natural" + "_eq" + str(n)
                file.write(f"      - {title}\n")
            if j == 2 or j == 3:
                title= "artificial" + "_gain"
            else:
                title= "natural" + "_gain"
            file.write(f"      - {title}\n")
