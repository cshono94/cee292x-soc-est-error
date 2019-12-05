#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 22:04:02 2019

Replot Timnah's Plots with Seaborn 

@author: coreyshono
"""


import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns


# Plot 1A Charge Cycle 
df = pd.read_csv("../results-plots/CSV-for-plots/1ACycler.csv", header=None) 
df.columns = ["Test(hr)", "SOC (%)"] 
df["Test(min)"] = df["Test(hr)"] * 60 


sns.lineplot(x="Test(min)", y="SOC (%)", data=df) 
plt.savefig("../results-plots/1ACycler.png", dpi=400)  
plt.close() 


# Load Regulation Cycles 
df_res1 = pd.read_csv("../results-plots/CSV-for-plots/RegD Signal 1/Res_reg d regulation signal 1.csv", header=None) 
df_bds1 = pd.read_csv("../results-plots/CSV-for-plots/RegD Signal 1/SOCBDS_reg d regulation signal 1.csv", header=None) 
df_pred1 = pd.read_csv("../results-plots/CSV-for-plots/RegD Signal 1/SOCPredict_reg d regulation signal 1.csv", header=None) 

df_res1.columns = ["Test(hr)", "SOC Residual (%)"] 
df_bds1.columns = ["Test(hr)", "SOC (%)"] 
df_pred1.columns = ["Test(hr)", "SOC (%)"] 

df_res1["Test(min)"] = df_res1["Test(hr)"] * 60 
df_bds1["Test(min)"] = df_bds1["Test(hr)"] * 60 
df_pred1["Test(min)"] = df_pred1["Test(hr)"] * 60 

df_res1 = df_res1.set_index("Test(min)") 
df_bds1 = df_bds1.set_index("Test(min)") 
df_pred1 = df_pred1.set_index("Test(min)") 

#df1 = pd.concat([df_bds1, df_res1], axis=1) 

df_res2 = pd.read_csv("../results-plots/CSV-for-plots/RegD Signal 2/Res_reg d regulation signal 2.csv", header=None) 
df_bds2 = pd.read_csv("../results-plots/CSV-for-plots/RegD Signal 2/SOCBDS_reg d regulation signal 2.csv", header=None) 
df_pred2 = pd.read_csv("../results-plots/CSV-for-plots/RegD Signal 2/SOCPredict_reg d regulation signal 2.csv", header=None) 

df_res2.columns = ["Test(hr)", "SOC Residual (%)"] 
df_bds2.columns = ["Test(hr)", "SOC (%)"] 
df_pred2.columns = ["Test(hr)", "SOC (%)"] 

df_res2["Test(min)"] = df_res2["Test(hr)"] * 60 
df_bds2["Test(min)"] = df_bds2["Test(hr)"] * 60 
df_pred2["Test(min)"] = df_pred2["Test(hr)"] * 60 

df_res2 = df_res2.set_index("Test(min)") 
df_bds2 = df_bds2.set_index("Test(min)") 
df_pred2 = df_pred2.set_index("Test(min)") 

# Plot SOC (%) plots for both BDS series 
plt.figure() 
sns.lineplot(x=df_bds1.index, y=df_bds1["SOC (%)"], label="RegD 1") 
sns.lineplot(x=df_bds2.index, y=df_bds2["SOC (%)"], label="RegD 2") 
plt.legend() 
plt.savefig("../results-plots/SOC_plot.png", dpi=400) 
plt.close() 

# Plot Resid plots for both Resid df's 
plt.figure() 
sns.lineplot(x=df_res1.index, y=df_res1["SOC Residual (%)"], label="RegD 1") 
sns.lineplot(x=df_res2.index, y=df_res2["SOC Residual (%)"], label="RegD 2") 
plt.legend() 
plt.savefig("../results-plots/resid_SOC_plot.png", dpi=400) 
plt.close() 







