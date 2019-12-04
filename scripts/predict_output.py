"""
This script takes the output_data pickle from read_output.py and fits the average
charge/discharge efficiencies, and also calculates the mapped efficiencies.
"""



#----------------------------------------------------------
# Import Libraries

import pandas as pd
import numpy as np
from sklearn import linear_model

#----------------------------------------------------------
# Define User Inputs

filename_output_data = "../results-pickles/pulse_50pct_pulse_50pct____0_NiMH_36s6p_output_data.P"
filename_output_data = "../results-pickles/norm_30sd40cap_2_norm_30sd40cap_2____0_NiMH_36s6p_output_data.P"
filename_output_data = "../results-pickles/pulse_merged_pulse_merged____0_NiMH_36s6p_output_data.P"

filename_test_data = "../results-pickles/norm_30sd40cap_2_norm_30sd40cap_2____0_NiMH_36s6p_output_data.P" 

Q_AH_NOM = 12.5 # Ah 


#----------------------------------------------------------
# Import Data

train_data = pd.read_pickle(filename_output_data)
test_data = pd.read_pickle(filename_test_data) 

fit_data = train_data[["Q", "Amps", "soc_eff"]].dropna()
test_data = test_data[["Q", "Amps", "soc_eff"]].dropna() 

#----------------------------------------------------------
# Split Data into charge and discharge 

def split_charge(data): 
    return data[data.Amps > 0], data[data.Amps < 0] 

[fit_c, fit_d] = split_charge(fit_data) 
[test_c, test_d] = split_charge(test_data) 

#----------------------------------------------------------
# Train Models 

def train_lm_model(fit, test):
    X_fit = fit[["Q", "Amps"]]
    y_fit = fit["soc_eff"] 
    
    X_test = test[["Q", "Amps"]] 
    y_test = test["soc_eff"] 
    
    m = linear_model.LinearRegression().fit(X_fit, y_fit) 
    
    print("Train Score: {}".format(m.score(X_fit, y_fit)))
    print("Test Score: {}".format(m.score(X_test, y_test))) 
    
    return m


eff_c_avg = fit_c["soc_eff"].mean() 
eff_d_avg = fit_d["soc_eff"].mean() 

model_c = train_lm_model(fit_c, test_c)
model_d = train_lm_model(fit_d, test_d) 


#----------------------------------------------------------
# Write Predict SOC update function 

def soc_update_avg(Q, I, dt, eff_c, eff_d): 
    """
    Returns next Q (SOC) given a fixed charge and discharge efficiency
    """ 
    if I > 0: 
        eff = eff_c
    elif I < 0: 
        eff = eff_d
    else: 
        eff = 1 
    
    return Q + (eff * I * dt) / Q_NOM * 100 

def soc_update_lm(Q, I, dt, m_c, m_d): 
    """
    Returns next Q (SOC) given a regressed charge and discharge efficiency
    """ 
    X = np.array([[Q, I]]) 
    if I > 0: 
        eff = m_c.predict(X)[0]
    elif I < 0: 
        eff = m_d.predict(X)[0] 
    else: 
        eff = 1
        
    return Q + (eff * I * dt) / Q_NOM * 100 




'''
#----------------------------------------------------------
# Evaluate Model

c_train_score =


chg_data = fit_data[fit_data.Amps > 0]
dchg_data = fit_data[fit_data.Amps < 0]


#----------------------------------------------------------
# Fit Efficiency as Linear Model of SOC, and Charge Rate

X = dchg_data[["Q", "Amps"]]
y = dchg_data["soc_eff"]

lm = linear_model.LinearRegression()
model = lm.fit(X,y)

y_preds = model.predict(X)
y_resid = y_preds - y

import matplotlib.pyplot as plt

#plt.plot(y, y_preds)
plt.hist(y_resid)


model.coef_
model.intercept_


'''
