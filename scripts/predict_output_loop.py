"""
This script takes the output_data pickle from read_output.py and fits the average
charge/discharge efficiencies, and also calculates the mapped efficiencies.
"""



#----------------------------------------------------------
# Import Libraries

import pandas as pd
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt 
import os

#----------------------------------------------------------
# Define User Inputs

#filename_output_data = "../results-pickles/pulse_50pct_pulse_50pct____0_NiMH_36s6p_output_data.P"
#filename_output_data = "../results-pickles/norm_30sd40cap_2_norm_30sd40cap_2____0_NiMH_36s6p_output_data.P"
#filename_output_data = "../results-pickles/pulse_merged_pulse_merged____0_NiMH_36s6p_output_data.P"

filename_output_data = "../results-pickles/rand_signals/norm_25sd40cap_1_norm_25sd40cap_1____0_NiMH_36s6p_output_data.P" 



#filename_test_data = "../results-pickles/norm_25sd40cap_1_norm_25sd40cap_1____0_NiMH_36s6p_output_data.P" 


filename_test_data = "../results-pickles/rand_signals/norm_25sd40cap_2_norm_25sd40cap_2____0_NiMH_36s6p_output_data.P" 
dir_in = "../results-pickles/rand_signals/" 
filepath_out = "../results-pickles/residuals_wNoise.P"

Q_AH_NOM = 12.5 # Ah 
precision = 0.001 # fraction of range (10-bit) 
#precision = 0.00024 # fraction of range (12-bit) 
sd_I = precision * 40

 
def soc_update_avg(Q, I, dt, eff_c, eff_d, sd_I=0): 
    """
    Returns next Q (SOC) given a fixed charge and discharge efficiency
    """ 
    if np.isnan(dt): 
        return Q 
    else: 
        if I > 0: 
            eff = eff_c
        elif I < 0: 
            eff = eff_d
        else: 
            eff = 1 
        I_err = np.random.normal(0,sd_I,1)[0] 
        return Q + (eff * -(I + I_err) * dt) / Q_AH_NOM * 100 

def soc_update_lm(Q, I, dt, m_c, m_d, sd_I=0): 
    """
    Returns next Q (SOC) given a regressed charge and discharge efficiency
    """ 
    if np.isnan(dt): 
        return Q 
    else: 
        X = np.array([[Q, I]]) 
        if I > 0: 
            eff = m_c.predict(X)[0]
        elif I < 0: 
            eff = m_d.predict(X)[0] 
        else: 
            eff = 1
            
        I_err = np.random.normal(0,sd_I,1)[0] 
        return Q + (eff * -(I+I_err) * dt) / Q_AH_NOM * 100 

def predict_soc(df, update_func, eff_c, eff_d, sd_I=0): 
    if update_func == soc_update_avg: 
        pred_col = "Q_pred_avg"
    elif update_func == soc_update_lm: 
        pred_col = "Q_pred_var"
    
    df[pred_col] = np.nan 
    
    # Initalize Q_pred
    df.loc[0, pred_col] = df.loc[0, "Q"] 
    
    # Step forward with Q_pred 
    for t in range(1, len(df)): 
        Q = df.loc[t-1, pred_col]
        I = df.loc[t-1, "Amps"]
        dt = df.loc[t-1, "step_hr"]
        if update_func == soc_update_avg: 
            df.loc[t, pred_col] = soc_update_avg(Q, I, dt, eff_c, eff_d, sd_I=sd_I) 
        elif update_func == soc_update_lm: 
            df.loc[t, pred_col] = soc_update_lm(Q, I, dt, eff_c, eff_d, sd_I=sd_I) 
        else: 
            continue 
        
    return df

def plot_resid(df): 
    df["pred_avg_resid"] = (df["Q_pred_avg"] - df["Q"].shift(1))
    df["pred_var_resid"] = (df["Q_pred_var"] - df["Q"].shift(1))
    
    #plt.figure(dpi=200) 
    '''
    plt.figure()
    plt.plot(df["Test(min)"], df["pred_avg_resid"], label="eff_avg", alpha=0.6) 
    plt.plot(df["Test(min)"], df["pred_var_resid"], label="eff_var", alpha=0.6) 
    plt.xlabel("Test (min)") 
    plt.ylabel("Residual (% SOC)") 
    plt.legend() 
    plt.tight_layout() 
    '''
    
    return df 


def split_charge(data): 
    return data[data.Amps > 0], data[data.Amps < 0] 

def train_lm_model(fit): #, test):
    X_fit = fit[["Q", "Amps"]]
    y_fit = fit["soc_eff"] 
    
    #X_test = test[["Q", "Amps"]] 
    #y_test = test["soc_eff"] 
    
    m = linear_model.LinearRegression().fit(X_fit, y_fit) 
    
    #print("Train Score: {}".format(m.score(X_fit, y_fit)))
    #print("Test Score: {}".format(m.score(X_test, y_test))) 
    
    return m


   
#----------------------------------------------------------
# Import Data

train_data = pd.read_pickle(filename_output_data)
#

fit_data = train_data[["Q", "Amps", "soc_eff"]].dropna()


#----------------------------------------------------------
# Split Data into charge and discharge 


[fit_c, fit_d] = split_charge(fit_data) 


#----------------------------------------------------------
# Train Models 

eff_c_avg = fit_c["soc_eff"].mean() 
eff_d_avg = fit_d["soc_eff"].mean() 

model_c = train_lm_model(fit_c) 
model_d = train_lm_model(fit_d) 

train_data = predict_soc(train_data, soc_update_avg, eff_c_avg, eff_d_avg, sd_I=sd_I) 
train_data = predict_soc(train_data, soc_update_lm, model_c, model_d, sd_I=sd_I) 


    

# Predict SOC 
filename_train_data = filename_output_data 
idx = 1 
for filename in os.listdir(dir_in): 
    print(filename) 
    if filename == filename_train_data: 
        continue 
    filename_test_data = os.path.join(dir_in, filename) 
    
    #----------------------------------------------------------
    
    test_data_full = pd.read_pickle(filename_test_data) 
    test_data = test_data_full[["Q", "Amps", "soc_eff"]].dropna() 
    [test_c, test_d] = split_charge(test_data) 
    
    #model_c = train_lm_model(fit_c, test_c)
    #model_d = train_lm_model(fit_d, test_d) 
    
    #----------------------------------------------------------
    # Write Predict SOC update function 
    
    #train_data = predict_soc(train_data, soc_update_avg, eff_c_avg, eff_d_avg) 
    #train_data = predict_soc(train_data, soc_update_lm, model_c, model_d) 
    
    test_data_full = predict_soc(test_data_full, soc_update_avg, eff_c_avg, eff_d_avg, sd_I=sd_I) 
    test_data_full = predict_soc(test_data_full, soc_update_lm, model_c, model_d, sd_I=sd_I) 
    
    train_data = plot_resid(train_data)
    test_data_full = plot_resid(test_data_full) 
    
    col_avg_name = "resid_eff_avg_{}".format(idx) 
    col_var_name = "resid_eff_var_{}".format(idx) 
    
    if idx == 1: 
        df_concat = test_data_full[["pred_avg_resid", "pred_var_resid", "Test(min)"]].set_index("Test(min)") 
    else: 
        df_concat = pd.concat([df_concat, test_data_full[["pred_avg_resid", "pred_var_resid", "Test(min)"]].set_index("Test(min)")], axis=1) 
        
    df_concat = df_concat.rename(columns={"pred_avg_resid": "pred_avg_resid_{}".format(idx), "pred_var_resid": "pred_var_resid_{}".format(idx)})
    
    idx += 1   

# Export Results
df_concat.to_pickle(filepath_out) 
                             


