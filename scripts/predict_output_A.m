% Use efficiency from previous cycler to predict SOC for a different charge cycle

%close all
clear all

%--------------------------------------------------------------------
% EDIT THIS INPUT (EFFICIENCY FROM READ_OUTPUT)
%--------------------------------------------------------------------

% Define efficiencies from analyzing simpler cycler; use to predict SOC in more complicated cycle
% Q(t) = Q(t-1) + effc*c*tstep - effd*d*tstep
effc = 0.988867898; % charge
effd =  1.00117765; % discharge
%effc = 1; % charge
%effd = 1; % discharge
%effc = 0.91
%effd = 0.86

%----------------------------------------------------------
% EDIT THIS INPUT (CYCLE CSV FILE)
%----------------------------------------------------------

% battery nominal values (must match input cycle to BDS)
%rated_cap = 1.1; % Ah, 18650 battery
rated_cap = 12.5; % Ah, NiMH ECM
%nom_Ah = 7; % for high-amp daily peaker cycle
%nom_A = 7; % max A charge rate, 18650 battery
%nom_V = 3.7; % V, 18650 battery
%nom_A = 30; % max A charge rate, 18650 battery (7 for 1, 2; 15 for 1b, 2b)
%nom_A = -30; % for 1c, 2c
nom_A = 100; % for battery pack

init_Ah = rated_cap*0.5; % start at 50% charge

% Load input files

% daily cycle 1
##filename = 'daily_peaker_profile.csv'; % cycler daily 1 (A)
##input = dlmread(filename, ',', 1, 0); % skip first 1 line
##time_hr = input(2:end,1); % skip first time
##SOC = nom_Ah.*input(:,2)./100; % total SOC in Ah
##charge_Ah = diff(SOC); % how much ADDED charge each time period
##charge_A = charge_Ah./time_hr; % charge rate over each time period

% reg 1
filename = 'regd-test-wave - Copy.csv';
input = dlmread(filename, ',', 2, 0); % skip first 2 lines
time_sec = input(:,2);
SOC = input(:,3); % normalized power
charge_A = nom_A.*SOC; % convert to A
step = 2; % seconds
time_hr = time_sec./3600;

% reg 2
##filename = 'reg d regulation signal.csv'; % cycler reg 2 (A)
##input = dlmread(filename, ',', 1, 0); % skip first 1 line
##time_min = input(:,1); % total time past
##time_min = time_min - time_min(1); % offset to start at zero
##SOC = nom_A*input(:,2); % in A (works up to 7.5*)
##% interpolation (reg 2)
##step = 5; % seconds
##time_sec = 0:step:50*60; % total time past; up to 50 minutes
##charge_A = interp1(time_min.*60,SOC,time_sec);
##time_hr = (step/3600)*ones(length(charge_A),1); % time step sizes

%----------------------------------------------------------
% Calculate predicted charge

time_total = [0;time_hr];
predict_Ah = zeros(1,length(time_hr)+1);
predict_Ah = init_Ah;
for i=1:length(time_hr)
  % get total time past, to compare to total time past in BDS simulation
  time_total(i+1) = time_total(i+1) + time_total(i);
  % get total SOC predicted by charge_A
  if charge_A(i) >= 0
    eff = effc; % charge
  else
    eff = effd; % discharge
  end
  predict_Ah(i+1) = predict_Ah(i) + eff*charge_A(i)*time_hr(i);
end
predict_SOC = predict_Ah./rated_cap.*100; % percent SOC

%----------------------------------------------------------
% EDIT THIS INPUT (CYCLE .OUT FILE)
%----------------------------------------------------------

% Cycler output 

data_start_line = 65; % first line of results data
%filename = 'Results/CyclerAReg1_CyclerAReg1____0_NiMH.out';
%filename = 'Results/CyclerAReg2_CyclerAReg2____0_NiMH.out';
filename = 'Results/CyclerAReg1b_CyclerAReg1b____0_NiMH.out';
%filename = 'Results/CyclerAReg2b_CyclerAReg2b____0_NiMH.out';

%data_start_line = 40;
%filename = 'Results/CyclerA1Day_CyclerA1Day____0_NiMH.out';

%----------------------------------------------------------
% Read cycler output

AllOutput = dlmread(filename, '\t', data_start_line-1, 0);
% get SOC output (as total energy stored in battery)
Q_idx = 29; % SOC as percent
%cycle_cap_idx = 13; % use this as SOC (total capacity in Ah stored)
%cycle_energy_idx = 16; % Wh
time = AllOutput(:,6); % hours
%cycle_capacity = -AllOutput(:,cycle_cap_idx); % take negative to make positive
%cycle_energy = -AllOutput(:,cycle_energy_idx);
cycle_SOC = AllOutput(:,Q_idx);

% View plot of charge/discharge cycle
view_plot = 0;
if view_plot == 1
  figure
  hold on
  plot(time,cycle_SOC,'-')
  title('SOC (Cycle)')
  xlabel('Time (hours)')
  ylabel('SOC (%)') %ylabel('Capacity (Ah)')
  set(gca,'FontSize',20)
  hold off
end
if view_plot == 1
  figure
  hold on
  plot(time_total,predict_SOC,'-')
  title('SOC (Predicted)')
  xlabel('Time (hours)')
  ylabel('SOC (%)') %ylabel('Capacity (Ah)')
  set(gca,'FontSize',20)
  hold off
end

%----------------------------------------------------------
% Plot predicted vs. simulated example

endtime = time_total(end);
timediff = endtime/time(end);
time = time.*timediff;

view_plot = 1;
if view_plot == 1
  figure
  hold on
  plot(time,cycle_SOC,'-')
  plot(time_total,predict_SOC,'-')
  title('SOC')
  xlabel('Time (hours)')
  ylabel('SOC (%)')
  legend('BDS Simulation','Predicted from Linear Efficiency Model','Location','Northeast')
  set(gca,'FontSize',20)
  hold off
end

%----------------------------------------------------------
% Calculate residuals

percent = 0; % if 1 find % error; if 0 find residual = absolute error

residuals = zeros(1,length(time_total));
for i=2:length(time_total)
  % get predicted value
  t = time_total(i);
  predict_val = predict_SOC(i); % changed from Ah to SOC
  % get simulated value
  j = find(time==t);
  if length(j) == 0
    % interpolate (linearly) to get simulated value at the same timestamp
    j = find(time>t)(1);
    k = j-1;
    frac = (t-time(k))/(time(j)-time(k));
    sim_val = cycle_SOC(k)*frac + cycle_SOC(j)*(1-frac); % changed from Ah to SOC
  else
    % exact time match; no interpolation needed
    j = j(1);
    sim_val = cycle_SOC(j); % changed from Ah to SOC
  end
  if percent == 1
    residuals(i) = (predict_val - sim_val)/predict_val;
  else
    residuals(i) = predict_val - sim_val;
  end
end

if view_plot == 1
  figure
  hold on
  plot(time_total,residuals,'o')
  title('Residuals')
  xlabel('Time (hours)')
  if percent == 1
    ylabel('% Error')
  else
    ylabel('Residual (% SOC)') % change label from Ah to SOC
  end
  set(gca,'FontSize',20)
  hold off
end


