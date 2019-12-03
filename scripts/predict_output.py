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


#----------------------------------------------------------
# Import Data 

output_data = pd.read_pickle(filename_output_data) 
fit_data = output_data[["Q", "Amps", "soc_eff"]].dropna() 


#----------------------------------------------------------
# Split Data into charge and discharge


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
