# ------------------------------------------------------------------------------
# Import Libraries

import pandas as pd
import os

# ------------------------------------------------------------------------------
# Define Functions 

def get_step_type(c):
    if c > 0:
        return "1"
    elif c < 0:
        return "2"
    else:
        return "3"

def get_control_type(c):
    if c != 0:
        return "1"
    else:
        return "0"

def get_control_value(c):
    return str(abs(c))


def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

def line_appender(filename, line):
    with open(filename, "a") as f:
        f.write(line)

# ------------------------------------------------------------------------------
# Define Filepaths

dir_in = "../cycles-raw/" 
dir_out = "../cycles-prg/" 

for idx in range(1, 9):

    file_in = "norm_25sd40cap_{}.csv".format(idx) 
    file_out = file_in.replace(".csv", ".prg")

    # ------------------------------------------------------------------------------
    # Read in raw cycle

    df = pd.read_csv(os.path.join(dir_in, file_in)) 
    n_steps = df.shape[0]

    # ------------------------------------------------------------------------------
    # Add prg variables


    df["step_type"] = df["Current(A)"].apply(get_step_type)
    df["control_type"] = df["Current(A)"].apply(get_control_type)
    df["control_value"] = df["Current(A)"].apply(get_control_value)
    df["end_type"] = 3
    df["end_value"] = df["Test(s)"].diff().shift(-1)
    df.iloc[-1,-1] = 10
    df["end_value"] = df["end_value"].astype(int).astype(str)
    df["limit_type"] = 0
    df["limit_value"] = 0
    df.iloc[-1,-1] = 10
    df["report_volts"] = 0.1
    df["report_time"] = 60
    df["report_temp"] = 25
    df.iloc[-1,-1] = 25
    df["last_col"] = 0
    df = df.astype(str)
    del df["Test(s)"]
    del df["Current(A)"]

    df



    # ------------------------------------------------------------------------------
    # Write cycle to .prg




    header_str = "Cycler\nVersion_1\n{}\n".format(n_steps)
    footer_str = """Oven
    Disabled
    0
    HTC	=	         100
    OVEN CONVECTION MODE	=	0
    Filter	=\t
    InitTemp	=	25"""

    df.to_csv(os.path.join(dir_out, os.path.join(dir_out, file_out)), sep="\t", header=False, index=False)
    line_prepender(os.path.join(dir_out, file_out), header_str)
    line_appender(os.path.join(dir_out, file_out), footer_str)
