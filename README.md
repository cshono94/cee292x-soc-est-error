# cee292x-soc-est-error

## Project Workflow 

### Generate Cycler File 
Starting with a CSV file input, generate a .prg output file that can run in BDS. CSV file shall 
have the following formating: 
- 2 columns in the following order: "Test(s)", "Current(A)" 
  - Test(s) is the number of seconds since the start of cycle 
  - Current(A) is the average current over from the current Test(s) until the next timestep 

Output .prg will have the following fields: 
- step type, control type, control value, end type, end value, limit type, limit value, report volts, report time, temperature(C)
  - step type: rest(3), charge(1), discharge(2)
  - control type: N/A(0), current(1)
  - control value: (in amps) 
  - end type: Time(3)
  - end value: number of seconds (10 for end) 
  - limit type: 0 
  - limit value: 0 (10 for end) 
  - report volts: 0.1 for all 
  - report time: 60 for all 
  - report temp: 25 for all 
  - last column (un-named): 0 for all 

### Run Cycler in BDS 
All is needed to run a simulation in BDS is a cylcer profile (.prg file) and a battery model (.smd). In this project a run in BDS is considered to be ground truth battery data. 
- Cycler Profile (.prg)
  - Generated in previous step 
- Battery Model (.smd)
  - Configure the number in series and parallel (36s80p) based on a Sonnen eco4 50V 4kWh battery 
  
### Fit model for a pulse cycle
- We will test a couple different pulse cycles: 
  - Constant current at 10% rated current for multiple pulses: 
    - From 50% SOC pulse charge up to 85% SOC
    - From 90% SOC pulse discharge down to 15% SOC 
    - From 10% SOC pulse charge up to 50% SOC 
  - Constant current at 50% rated current for multiple pulses: 
    - From 50% SOC pulse charge up to 85% SOC 
    - From 85% SOC pulse discharge down to 15% SOC 
    - From 15% SOC pulse charge up to 50% SOC 
  - Constant current at 100% rated current for multiple pulses: 
    - From 50% SOC puls charge up to 85% SOC 
    - From 85% SOC pulse discharge down to 15% SOC 
    - From 15% SOC pulse charge up to 50% SOC 
  - Sequentially run all of the above charge cycles in one simulation 
- After results for fitting cycle are obtained: 
  - Fit a single charge and discharge efficiency for the entire charge cycle 
  - Fit piecewise efficiency mapped to SOC, current, and Temp(C) 
- Predict SOC using fitted models on the training data 
  - Add error measure for predicting actual uncertainty 
  - Q(t+1) = Q(t) + eff x (C + error) 
  - Q(t+1) = Q(t) + eff(Q, C, T) x (C + error) 
- Predict SOC using fitted models on a test cycle (regulation signal, etc...) 
