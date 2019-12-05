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

