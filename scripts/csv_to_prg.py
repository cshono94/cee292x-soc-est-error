# ------------------------------------------------------------------------------
# Import Libraries

import pandas as pd

# ------------------------------------------------------------------------------
# Define Filepaths

file_in = "../cycles-raw/pulse_100pct.csv"
file_out = "../cycles-prg/pulse_100pct.prg"

# ------------------------------------------------------------------------------
# Read in raw cycle

df = pd.read_csv(file_in)
df.shape

# ------------------------------------------------------------------------------
# Add prg variables

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
        return ""

def get_control_value(c):
    return str(abs(c))

df["step_type"] = df["Current(A)"].apply(get_step_type)
df["control_type"] = df["Current(A)"].apply(get_control_type)
df["control_value"] = df["Current(A)"].apply(get_control_value).replace("0", "")
df["end_type"] = 3
df["end_value"] = df["Test(s)"].diff().shift(-1)
df.iloc[-1,-1] = 10
df["end_value"] = df["end_value"].astype(int).astype(str)
df["limit_type"] = 0
df["limit_value"] = 0
df.iloc[-1,-1] = 10
df["report_volts"] = 0.1
df["report_temp"] = 25
df["last_col"] = 0
df = df.astype(str)
del df["Test(s)"]
del df["Current(A)"]

df



# ------------------------------------------------------------------------------
# Write cycle to .prg

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)


header_str = "Cycler\nVersion_1\n1201\n"
df.to_csv(file_out, sep="\t", header=False, index=False)
line_prepender(file_out, header_str)
