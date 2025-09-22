#================================================================================
#================================================================================
# SONUS CORRECT
#================================================================================
#================================================================================
import sys
import os
import pandas as pd
import yaml
import tkinter as tk
from tkinter import filedialog
from tkinter import Tk, ttk
from ttkthemes import ThemedTk
from pathlib import Path

import FriCalc
import TargetCalc
import EqMake
import Math
import Utils

from Utils import write_eq_settings_yml0, write_eq_settings_yml2, write_eq_settings_yml3

Ver = "1.10"

def config_file_path(relative_path: str) -> str:
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Exit Python when window is closed
def close_window():
    root.destroy()
    root.quit()
    
    
# Function to read data from a YAML file and display it in the GUI
def load_yaml():
    global data_config
    with open(config_file_path, "r", encoding="utf-8") as f:
        data_config = yaml.safe_load(f)

    if data_config is None:
        data_config = {}
        
    # Specify the order in which they are displayed on the GUI
    order = [
        'output_folder',
        'data_file',
        'eloud_file',
        'hrtf_file',
        'eq1_file',
        'eq2_file',
        'eq_file_yml',
        'lr',
        'slope',
        'band_num',
        'max_q',
        'min_q',
        'default_q',
        'low_cutoff1',
        'high_cutoff1',
        'low_cutoff2',
        'high_cutoff2',
        'target',
        'dip_alpha',
    ]
    
    # Get the order of keys in data_config and use it as parameter_order
    global parameter_order
    parameter_order = list(order)

# Function to save data to a YAML file
def save_yaml():
    with open(config_file_path, "w", encoding="utf-8") as f:
        yaml.dump(data_config, f)

# Function to store data
def save_data():
    for key, entry in entries.items():
        # For numeric data, convert to float type and save
        if key == 'band_num':
            try:
                data_config[key] = int(entry.get())
            except ValueError:
                # If it cannot be converted to numerical values, save as is
                data_config[key] = entry.get()
        elif key in numeric_keys:
            try:
                data_config[key] = float(entry.get())
            except ValueError:
                # If it cannot be converted to numerical values, save as is
                data_config[key] = entry.get()
        else:
            # If it cannot be converted to numerical values, save as is
            data_config[key] = entry.get()
    save_yaml()       
    
def open_file_dialog(entry_widget):
    path = Path(entry_widget.get())
    if path:
        file_path = filedialog.askopenfilename(initialdir=path.parent)
    else:
        file_path = filedialog.askopenfilename(initialdir=Path.cwd())
        
    if file_path:
        entry_widget.delete(0, tk.END)  # Delete current contents of entry widget
        entry_widget.insert(0, file_path)  # Insert selected file path

def open_folder_dialog(entry_widget):
    path = Path(entry_widget.get())
    if path:
        folder_path = filedialog.askdirectory(initialdir=path)
    else:
        folder_path = filedialog.askdirectory(initialdir=Path.cwd())
        
    if folder_path:
        entry_widget.delete(0, tk.END)  # Delete current contents of entry widget
        entry_widget.insert(0, folder_path)  # Insert selected folder path
        
# Function to create GUI----------------------------------------------------------------------------
def create_gui():
    global root
    root = ThemedTk(theme='adapta')
    root.title("SonusCorrect Ver." + str(Ver))
    root.protocol("WM_DELETE_WINDOW", close_window)
    load_yaml()
    
    # Create custom fonts
    font = ("Meiryo", 10)  # Specify font name and size
    font_b = ("consolas", 10, "bold")
    # Set Japanese font
    font_jp = ("Meiryo", 10)
    
    # Window Size
    root.geometry("1010x980")
    
    # Make window height unchangeable
    root.resizable(width=False, height=False)
    
    # Padding to set the interval at which each piece of data is displayed
    row_padding = 2
    
    parent = ttk.Frame(root)
    parent.pack(fill="both", expand="yes")
    
    # Create and place new labels
    ttk.Label(parent, text=' [Output Folder] --------------------------------------------------------------------------------------------------------------------------', font=font_b).grid(row=0, column=0, columnspan=3, sticky="w", pady=5, padx=0)
    ttk.Label(parent, text=' [Input Data] -----------------------------------------------------------------------------------------------------------------------------', font=font_b).grid(row=2, column=0, columnspan=3, sticky="w", pady=5, padx=0)
    ttk.Label(parent, text=' [Output File Name] -----------------------------------------------------------------------------------------------------------------------', font=font_b).grid(row=6, column=0, columnspan=3, sticky="w", pady=5, padx=0)
    ttk.Label(parent, text=' [Frequency Response Of The Music Track] ------------------------------------------------------------------------------', font=font_b).grid(row=11, column=0, columnspan=3, sticky="w", pady=5, padx=0)
    ttk.Label(parent, text=' [Make EQ Curves] -------------------------------------------------------------------------------------------------------------------------', font=font_b).grid(row=13, column=0, columnspan=3, sticky="w", pady=5, padx=0)
    ttk.Label(parent, text=' ', font=font_b).grid(row=24, column=0, columnspan=3, sticky="w", pady=0, padx=0)
    
    entry_frames = []
    
    # Display each data
    row_index = 0
    for key in parameter_order:
        if row_index == 0 or row_index == 2 or row_index == 6 or row_index == 11 or row_index == 13:
            row_index += 1
        
        value = data_config.get(key, "")
        description = parameter_descriptions.get(key, "No description available")
        label = ttk.Label(parent, text=f"{description}:", font=font)
        label.grid(row=row_index, column=0, sticky="e", pady=5, padx=0)
        
        if key in file_path_keys or key in folder_path_keys:
            entry_frame = ttk.Frame(parent)
            entry_frame.grid(row=row_index, column=1,  columnspan=2, sticky="ew", pady=row_padding, padx=5)
            entry_frames.append(entry_frame)
            
            value = int(data_config.get(key, "")) if isinstance(data_config.get(key, ""), int) else data_config.get(key, "")
            entry = ttk.Entry(entry_frame, width=80, font=font)
            entry.insert(0, str(value))
            entry.grid(row=0, column=0, sticky="ew") 
            entries[key] = entry
            
            button_text = "File" if key in file_path_keys else "Folder"
            if key in file_path_keys:
                button = ttk.Button(entry_frame, text="File", command=lambda entry=entry: open_file_dialog(entry))
            else:
                button = ttk.Button(entry_frame, text="Folder", command=lambda entry=entry: open_folder_dialog(entry))
            button.grid(row=0, column=2, padx=None)
            
        elif key in file_name_keys:
            entry = ttk.Entry(parent, width=30, font=font)
            entry.insert(0, str(value))
            entry.grid(row=row_index, column=1, sticky="w", pady=row_padding, padx=5)
            entries[key] = entry
        else:
            entry = ttk.Entry(parent, width=20, font=font)
            entry.insert(0, str(data_config.get(key, "")))
            entry.grid(row=row_index, column=1, sticky="w", pady=row_padding, padx=5)
            entries[key] = entry
        
        com = param_com.get(key, "No Comment")
        label = ttk.Label(parent, text=f"{com}", font=font_jp)
        label.grid(row=row_index, column=2, sticky="w", pady=5, padx=5)
            
        row_index += 1
    
    # Create Save button
    button_save = ttk.Button(parent, text='Save to Config File', command=save_data)
    button_save.grid(row=row_index + 1, column=0, columnspan=3, pady=8)
    
    # Create "Run Calculate" button
    button_ok = ttk.Button(parent, text='Run Calculate', command=calculate)
    button_ok.grid(row=row_index + 2, column=0, columnspan=3, pady=8)
    row_index += 1
    
    root.mainloop()

# Main calculation-----------------------------------------------------------------------------
def calculate():
    global data_config
    
    #Processing when the OK button is pressed
    save_data()
    
    with open(config_file_path,'r', encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    #INPUT==========================================================================
    output_folder = Path(config['output_folder'])
    eloud_file     = Path(config['eloud_file'])      
    data_file  = Path(config['data_file'])   
    #out        = str(config['out'])         
    slope      = float(config['slope'])       
    hrtf_file  = Path(config['hrtf_file'])
    #================================================================================
    band_num  =  int(config['band_num'])    
    eq1_file  =  str(config['eq1_file'])    
    eq2_file  =  str(config['eq2_file'])
    eqyml_file = str(config['eq_file_yml'])
    lr         = str(config['lr'])
    model_str =  str(config['data_file'])  

    max_q     =  float(config['max_q'])
    min_q     =  float(config['min_q']) 
    default_q =  float(config['default_q']) 

    window_oct = 0.1
    
    low_cutoff1 = float(config['low_cutoff1'])  # Low frequency cutoff [Hz]
    high_cutoff1 = float(config['high_cutoff1'])  # High frequency cutoff [Hz]
    
    low_cutoff2 = float(config['low_cutoff2'])  # Low frequency cutoff [Hz]
    high_cutoff2 = float(config['high_cutoff2'])  # High frequency cutoff [Hz]

    target = float(config['target']) 
    
    dip_alpha = float(config['dip_alpha']) 

    
    # Get script file directory
    script_dir = Path.cwd()
    
    # Make file paths absolute
    file2_path   = eloud_file.resolve()
    file3_path   = data_file.resolve()
    target_calclated_path = output_folder.resolve().joinpath("target_curve_natural_flat.txt")
    hrtf_path    = hrtf_file.resolve()
    #out_path     = output_folder.resolve().joinpath(out)
    
    print("================================================================================")
    print("================================================================================")
    print("                                 SONUS CORRECT")
    print("           Eq Data Creation Program for Sound Field Correction")
    print("                                           Made By Quick-Waipa")
    print("                                                      Ver." + Ver)
    print("================================================================================")
    print("================================================================================")
    print("")
    
    
    
    # Frequency response data with slope+ iso-loudness curve applied in TargetCalc.py=========
    TargetCalc.target_calc(file2_path, output_folder, slope, hrtf_path)
    
    # EQ Data Creation=======================================================
    # flat target--------------------------------------------------
    target_type = "artificial"
    eq1_path    = output_folder.joinpath(eq1_file)
    eq_path_yml = output_folder.joinpath(eqyml_file)

    write_eq_settings_yml0(eq_path_yml, target_type)
    
    data = {'band_num':band_num,
            'file_path':file3_path,
            'out_path':eq1_path,
            'out_path_yml':eq_path_yml,
            'lr':lr,
            'model_str':model_str,
            'max_q':max_q,
            'min_q':min_q,
            'default_q':default_q,
            'window_oct':window_oct,
            'low_cutoff':low_cutoff1,
            'high_cutoff':high_cutoff1,
            'target':target,
            'target_path':"",
            'out':'plot_artificial_',
            'output_folder':output_folder,
            'target_on':False,
            'dip_alpha':dip_alpha,
            'target_type':target_type,
            #'hrtf_path':'',
    }
    EqMake.eq_make(data)
    
    fri_k1, fri_f1, diff = FriCalc.fri_calc(eq1_path, file3_path, file2_path, slope)
    
    write_eq_settings_yml2(eq_path_yml, target_type, diff)
    
    # slope - equal loudness curve target-------------------------------------
    target_type = "natural"
    eq2_path   = output_folder.joinpath(eq2_file)
    
    data2 = {'band_num':band_num,
            #'file_path':out_path,
            'file_path':file3_path,
            'out_path':eq2_path,
            'out_path_yml':eq_path_yml,
            'lr':lr,
            'model_str':model_str,
            'max_q':max_q,
            'min_q':min_q,
            'default_q':default_q,
            'window_oct':window_oct,
            'low_cutoff':low_cutoff2,
            'high_cutoff':high_cutoff2,
            'target':target,
            'target_path':target_calclated_path,
            'out':'plot_natural_',
            'output_folder':output_folder,
            'target_on':True,
            'dip_alpha':dip_alpha,
            'target_type':target_type,
            #'hrtf_path':hrtf_path,
    }
    EqMake.eq_make(data2)
    
    fri_k1, fri_f1, diff = FriCalc.fri_calc(eq2_path, file3_path, file2_path, slope)
    
    write_eq_settings_yml2(eq_path_yml, target_type, diff)
    
    write_eq_settings_yml3(eq_path_yml, lr, band_num)
    
    #Calculate gain increase/decrease after applying EQ filter in EqCalc.py===========================
    print("================================================")
    print("Calculate Frequency Response Integral:FRI")
    print("================================================")
    print("Artificial Flat Target FR Data")
    fri_k1, fri_f1, fri_diff1 = FriCalc.fri_calc(eq1_path, file3_path, file2_path, slope)
    print("------------------------------------------------")
    print("fri_before_EQ-filter[dB]: ", fri_k1)
    print("fri_after_EQ-filter [dB]: ", fri_f1)
    print("fri_diff:           [dB]: ", fri_diff1)
    print("------------------------------------------------")
    print("Natural Flat Target FR Data")
    fri_k2, fri_f2, fri_diff2 = FriCalc.fri_calc(eq2_path, file3_path, file2_path, slope)
    print("------------------------------------------------")
    print("fri_before_EQ-filter[dB]: ", fri_k2)
    print("fri_after_EQ-filter [dB]: ", fri_f2)
    print("fri_diff:           [dB]: ", fri_diff2)
    print("------------------------------------------------")
    
    with open("fri.txt", "w") as f:
        f.write("================================================\n")
        f.write("Calculate Frequency Response Integral:FRI\n")
        f.write("================================================\n")
        f.write("Artificial Flat Target FR Data\n")
        f.write("------------------------------------------------\n")
        f.write("fri_before_equalization[dB]: " + str(fri_k1) + "\n")
        f.write("fri_after_equalization [dB]: " + str(fri_f1) + "\n")
        f.write("fri_diff:              [dB]: " + str(fri_diff1) +"\n")
        f.write("------------------------------------------------\n")
        f.write("Natural Flat Target FR Data\n")
        f.write("------------------------------------------------\n")
        f.write("fri_before_equalization[dB]: " + str(fri_k2) + "\n")
        f.write("fri_after_equalization [dB]: " + str(fri_f2) + "\n")
        f.write("fri_diff:              [dB]: " + str(fri_diff2) + "\n")
        f.write("------------------------------------------------\n")
    
    # Move and overwrite files
    os.replace("fri.txt", output_folder.joinpath("fri.txt"))
    
    print("Calculation completed successfully.")
    
    
# main function--------------------------------------------------------------------------------------------
def main():
    # Create and run a GUI
    global config_file_path
    global entries, data_config, numeric_keys, parameter_descriptions, param_com, folder_path_keys, file_path_keys, file_name_keys
    entries = {}
    data_config = {}
    config_file_path = config_file_path("config.yaml")
    numeric_keys = ['slope', 'band_num', 'max_q', 'min_q', 'default_q',
                    'low_cutoff1', 'high_cutoff1',
                    'low_cutoff2', 'high_cutoff2', 'target']
    
    # Title of each parameter
    parameter_descriptions = {
        'output_folder': ' Output Folder Path',
        'eloud_file': ' Equal loudness contour Data File Path',
        'data_file': ' Speaker FR Data File Path',
        #'out': ' Filter Applied FR Data File Name',
        'slope': ' Slope [dB/oct]',
        'band_num': ' Band Number',
        'eq1_file': ' EQ (artificial flat target) File Name',
        'eq2_file': ' EQ (natural flat target) File Name',
        'eq_file_yml': ' EQ data file .yml (for Mac)',
        'lr': ' Left or Right',
        'max_q': ' Max Q [-]',
        'min_q': ' Min Q [-]',
        'default_q': ' Default Q [-]',
        'low_cutoff1': ' Low Cutoff (artificial flat target) [Hz]',
        'high_cutoff1': ' High Cutoff (artificial flat target) [Hz]',
        'low_cutoff2': '      Low Cutoff (natural flat target) [Hz]',
        'high_cutoff2': ' High Cutoff (natural flat target) [Hz]',
        'target': ' EQ Creating Target Level [dB]',
        'dip_alpha':' How Much to Fill the Dip',
        'hrtf_file':' HRTF File Path',
    }

    # Comment text corresponding to each parameter
    param_com = {
        'output_folder': '',
        'eloud_file': '',
        'data_file': '',
        'hrtf_file':'',
        'slope': 'Slope of reference sound source.(Reference: Pink noise: -3 dB/oct)',
        'band_num': 'Number of EQ Bands',
        'eq1_file': 'File name for saving EQ data (artificial flat target)',
        'eq2_file': 'File name for saving EQ data (natural flat target)',
        'eq_file_yml': 'EQ data file .yml (for Mac)',
        'lr': 'Left speaker or Right speaker ["L" or "R"]',   
        'max_q': 'Maximum Q factor',
        'min_q': 'Minimum Q factor',
        'default_q': 'Q factor to be set for now in case of calculation error',
        'low_cutoff1': 'Lower limit of frequency cutoff when creating EQ (artificial flat target)',
        'high_cutoff1': 'Upper frequency cutoff limit when creating EQ (artificial flat target)',
        'low_cutoff2': 'Lower limit of frequency cutoff when creating EQ (natural flat target)',
        'high_cutoff2': 'Upper frequency cutoff limit when creating EQ (natural flat target)',
        'target': 'Target level when creating EQ',
        'dip_alpha':'How much to fill the dip (0.0 to 1.0)',
    }
    
    # Key to data from which file paths can be selected
    folder_path_keys = ['output_folder']
    file_path_keys = ['eloud_file', 'data_file', 'target_file', 'hrtf_file']
    #file_name_keys = ['out','eq1_file','eq2_file']
    file_name_keys = ['eq1_file','eq2_file']
    create_gui()
    
    
if __name__ == "__main__":
    main()