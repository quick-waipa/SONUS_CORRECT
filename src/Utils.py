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