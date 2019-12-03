# Read BDS ouptut file

#----------------------------------------------------------
# Import Libraries

import pandas as pd
import numpy as np
import os
import plotly.offline as pyo
import plotly.graph_objs as go

#----------------------------------------------------------
#----------------------------------------------------------
# DEFINE USER INPUTS HERE
# ALL OF THESE ITEMS CHANGE DEPENDING ON BDS SIMULATION RUN
#----------------------------------------------------------
#----------------------------------------------------------

# Define nominal (intended) charge/descharge rate (copy from BDS)

filename = "./Results/Cycler4_Cycler4____0_NiMH____1.out"
data_start_line = 24
q_nom = 12.5 # Ah

filename = "../bds-out/pulse_10pct_pulse_10pct____0_NiMH_36s6p.out"
data_start_line = 65
q_nom = 12.5 # Ah

filename = "../bds-out/pulse_50pct_pulse_50pct____0_NiMH_36s6p.out"
data_start_line = 65
q_nom = 12.5

filename = "../bds-out/pulse_100pct_pulse_100pct____0_NiMH_36s6p.out"
data_start_line = 65
q_nom = 12.5

filename = "../bds-out/norm_30sd40cap_2_norm_30sd40cap_2____0_NiMH_36s6p.out"
data_start_line = 65
q_nom = 12.5

filename = "../bds-out/pulse_merged_pulse_merged____0_NiMH_36s6p.out" 
data_start_line = 65
q_nom = 12.5 

#----------------------------------------------------------
# Generate output filenames

filename_str = filename.split("/")[-1].split(".out")[0]
filename_plot = "../results-plots/" + filename_str + "_plot.html"
filename_socplot = "../results-plots/" + filename_str + "_SOCplot.html"
filename_pickle = "../results-pickles/" + filename_str + "_output_data.P"

#----------------------------------------------------------
# Define Read Functions

def add_sign_to_current(row):
    if "Charge" in row["Type"]:
        return -row["Current_A"]
    else:
        return row["Current_A"]
def read_input(filepath):
    input_data = pd.read_csv(filepath, sep='|', header=None, skiprows=8, nrows=50)
    input_data = input_data.iloc[:,[2,4,6]]
    input_data.columns = ["Type", "Current_A", "Time_s"]
    input_data["Current_A"] = input_data["Current_A"].apply(lambda s: float(s.replace("A","").replace("W","")))
    input_data["Current_A"] = input_data.apply(add_sign_to_current, axis=1)

    input_data["Time_s"] = input_data["Time_s"].apply(lambda s: float(s.split("s")[0]))
    input_data["Step_s"] = input_data["Time_s"].copy()
    input_data["Time_s"] = input_data["Time_s"].cumsum()

    input_data = input_data.rename(columns = {"Current_A": "Power_W"})
    if "Power_W" in input_data:
        input_data["step_wh_in_cycler"] = input_data["Power_W"] * input_data["Step_s"] / 3600
    else:
        input_data["step_ah_in_cycler"] = input_data["Current_A"] * input_data["Step_s"] / 3600
    return input_data

def read_prg(filepath):
    df = pd.read_csv(filepath, header=None, skiprows=3, sep="\t")
    df = df.iloc[:602,[2,4]]
    print(df.shape)
    df.columns = ["Amps", "step_s"]

    # Calculate Columns
    df["step_hr"] = df["step_s"] / 3600
    df["step_ah_in"] = df["Amps"] * df["step_hr"]
    df["test_s"] = df["step_s"].cumsum()

    return df

def try_float(s):
    try:
        return float(s)
    except:
        return 0

def read_nimh_output(filepath):
    headers = [
        "Rec#", "Cyc#", "Step", "StepType", "Mode", "Test(min)", "Step(min)", "Volts",
        "Amps", "T(C)", "Pressure(atm)", "StepCapacity", "CycleCapacity(Ah)", "CumCapacity(Ah)",
        "StepEnergy(Wh)", "CycleEnergy(Wh)", "CumEnergy(Wh)", "HeatGen(W)", "tStep(S)",
        "Tamb(C)", "dQdV(C/V)", "SimTime(min)", "V2", "Voc", "Vh", "V1", "I1", "I2",
        "Q", "Sd", "RTime(min)"
    ]

    headers_subset = [
        "Step", "Test(min)", "Amps", "Mode", "CumCapacity(Ah)", "CumEnergy(Wh)",
        "Q", "T(C)" 
    ]

    output_data = pd.read_csv(filepath, sep='\t', header=None, skiprows=data_start_line-1)
    output_data.columns = headers
    output_data = output_data[headers_subset]

    # Calculate Columns
    output_data["Test(min)"] = output_data["Test(min)"].astype(float)

    output_data["test_s"] = output_data["Test(min)"]*60
    output_data["test_hr"] = output_data["Test(min)"]/60
    output_data["Step(min)"] = output_data["Test(min)"].diff()
    output_data["step_s"] = output_data["Step(min)"]*60
    output_data["step_hr"] = output_data["Step(min)"]/60
    output_data["step_ah_in"] = -output_data["Amps"] * output_data["step_hr"]
    output_data["step_ah_cumdelta"] = output_data["CumCapacity(Ah)"].diff()
    output_data["test_ah_soc"] = output_data["Q"] / 100 * q_nom
    output_data["step_ah_soc"] = output_data["test_ah_soc"].diff()

    output_data["soc_eff"] = output_data["step_ah_soc"] / output_data["step_ah_in"]
    output_data["soc_eff"] = output_data["soc_eff"].apply(replace_eff_outliers)


    return output_data

def replace_eff_outliers(eff):
    if (eff > 1.05) | (eff < 0.95):
        return np.nan
    else:
        return eff

def plot_traces(output_data):

    trace_ah_in = go.Scatter(
        x = output_data["Test(min)"],
        y = output_data["step_ah_in"],
        name = "Charge Cycle (Ah)",
        opacity = 0.66,
    )

    trace_ah_soc = go.Scatter(
        x = output_data["Test(min)"],
        y = output_data["step_ah_soc"],
        name = "delta_SOC (Ah)",
        opacity = 0.66
    )

    trace_ah_eff = go.Scatter(
        x = output_data["Test(min)"],
        y = output_data["soc_eff"],
        name = "Ah Efficiency",
        opacity = 0.66,
        yaxis = "y2"
    )

    layout = go.Layout(
        xaxis = dict(title = "Test (min)"),
        yaxis = dict(title="Delta Capacity (Ah)"),
        yaxis2 = dict(
            title = "Step Efficiency",
            overlaying = "y",
            side = "right"
        )
    )

    fig = go.Figure(data=[trace_ah_in, trace_ah_soc, trace_ah_eff], layout=layout)
    pyo.plot(fig, auto_open=False, filename=filename_plot)

    trace_soc = go.Scatter(
        x = output_data["Test(min)"],
        y = output_data["test_ah_soc"]/q_nom*100,
        name = "SOC (%)"
    )

    layout = go.Layout(
        xaxis = dict(title = "Test (min)"),
        yaxis = dict(title = "SOC (%)"),
    )

    fig_soc = go.Figure(data=[trace_soc], layout=layout)
    pyo.plot(fig_soc, auto_open=False, filename=filename_socplot)

#----------------------------------------------------------

# Main

# Read output and calculate efficiencies
output_data = read_nimh_output(filename)

# Plot Results
plot_traces(output_data)

# Export output_data to pickle
output_data.to_pickle(filename_pickle)
