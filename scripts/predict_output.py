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

X = chg_data[["Q"]]#, "Amps"]] 
y = chg_data["soc_eff"] 

#lm = linear_model.LinearRegression()
#model = lm.fit(X,y)

from statsmodels.api import OLS
m = OLS(y,X).fit() 


import matplotlib.pyplot as plt 
plt.hist(m.resid) 
print(m.summary())








