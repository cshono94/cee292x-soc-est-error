% Read BDS output file
% Calculate efficiency, and residuals
% Uses % SOC
% Output must be from cycle with at least one constant charge and one constant discharge block

%close all
clear all
%nom_V = 3.7;
rated_cap = 12.5; % Ah, NiMH ECM

%----------------------------------------------------------
%----------------------------------------------------------
% DEFINE USER INPUTS HERE
% ALL OF THESE ITEMS CHANGE DEPENDING ON BDS SIMULATION RUN
%----------------------------------------------------------
%----------------------------------------------------------

% Define nominal (intended) charge/discharge rate (copy from BDS cycler)
##nom_charge = [1, 2, 0.5]; % W
##nom_discharge = [-2, -3, -1];
##total_blocks = 12; % number of steps in cycler
##charge_blocks = [1, 7, 11]; % which steps/lines you defined as charging in the BDS simulation cycler
##discharge_blocks = [3, 5, 9]; % which lines you defined as discharging
##data_start_line = 28; % what line of results txt file does actual data start on
##filename = 'Results/old/_Test[Cycler2]_Proc[Cycler2]_Cell[hp18650Spiral-DIST].out';

% charge/discharge repeated 3 times at constant A (or W)
nom_charge = [1,1,1]; % A
nom_discharge = [-1,-1,-1]; % discharge is negative
total_blocks = 6; % number of steps in cycler
charge_blocks = [1,3,5];
discharge_blocks = [2,4,6];
data_start_line = 22;
%filename = 'Results/Cycler1A_Cycler1A____0_NREL2RC.out';
filename = 'Results/Cycler1A_Cycler1A____0_NiMH.out';
%filename = 'Results/_Test[Cycler1A]_Proc[Cycler1A]_Cell[hp18650Spiral-DIST]____1.out';

%----------------------------------------------------------

% Load inputs

AllOutput = dlmread(filename, '\t', data_start_line-1, 0);

% Define charge/discharge times
times = dlmread(filename, '|', 8, 0); % time is 8th column of header table
times = times(1:total_blocks,7)./3600; % convert to hours
times = [0, times']; % starts at time zero; also, convert to row vector
for i=2:length(times)
  times(i) = times(i) + times(i-1); % cumulative
end
charge_start_times = times(charge_blocks);
charge_end_times = times(charge_blocks+1);
discharge_start_times = times(discharge_blocks);
discharge_end_times = times(discharge_blocks+1);
ncharge = length(charge_start_times);
ndischarge = length(discharge_start_times);

%cycle_cap_idx = 13; % idx of total Ah stored
%cum_cap_idx = 14;
%cycle_energy_idx = 16; % use this as SOC (total energy in Wh stored)
%cum_energy_idx = 17;
%volt_idx = 8;
Q_idx = 29; % SOC as percent

% Get SOC output (as total energy stored in battery)

time = AllOutput(:,6)./60; % convert from minutes to hours
%cycle_energy = -AllOutput(:,cycle_energy_idx); % take negative to make positive
cycle_SOC = AllOutput(:,Q_idx);

% View plot of charge/discharge cycle

view_plot = 1;
if view_plot == 1
  figure;
  hold on;
  plot(time,cycle_SOC,'-')
  title('SOC (Cycle)')
  xlabel('Time (hours)')
  ylabel('SOC (%)')
  hold off;
  set(gca,'FontSize',20)
end

%----------------------------------------------------------

% Get charge and discharge portions separately

charge_start = []; charge_end = []; discharge_start = []; discharge_end = [];

% Find specific charge and discharge start/end indices (note: column vectors)
for i=1:ncharge
  charge_start = [charge_start, find(time>=charge_start_times(i))(1)];
  charge_end = [charge_end, find(time>=charge_end_times(i))(1)-1];
end
for i=1:ndischarge
  discharge_start = [discharge_start, find(time>=discharge_start_times(i))(1)];
  discharge_end = [discharge_end, find(time>=discharge_end_times(i))(1)-1];
end

% check by adding to plot
view_plot = 0;
if view_plot == 1
  hold on
  plot(time(charge_start),cycle_SOC(charge_start),'bo','MarkerSize',10)
  plot(time(charge_end),cycle_SOC(charge_end),'bo','MarkerSize',10)
  plot(time(discharge_start),cycle_SOC(discharge_start),'ko','MarkerSize',10)
  plot(time(discharge_end),cycle_SOC(discharge_end),'ko','MarkerSize',10)
  hold off
end


%----------------------------------------------------------
% Calculate actual avg charge rate in W

% Get slope (i.e. charge rate) from each block
charge_rate = zeros(1,ncharge);
discharge_rate = zeros(1,ndischarge);

% use 2 for getting residuals later; others not implemented
method = 2; % 1 if linear regression, 2 if linear regression with forced (0,0),
            % 3 if slope over endpoints (min/max of charge cycle)

% store each charge/discharge portion for later
Xcharge = {}; Ycharge = {}; Tcharge = zeros(1,ncharge);
Xdischarge = {}; Ydischarge = {}; Tdischarge = zeros(1,ndischarge);

% Charge
for i=1:ncharge
  % start and end indices of this charge portion
  idx1 = charge_start(i);
  idx2 = charge_end(i);
  % fit linear charge rate
  if method == 2 % linear regression forced through 0,0
    X = time(idx1:idx2)(:) - time(idx1); % offset to zero
    Y = cycle_SOC(idx1:idx2)(:) - cycle_SOC(idx1); % offset to zero
    Xcharge{end+1} = X; Ycharge{end+1} = Y;
    B = X\Y;
    charge_rate(i) = B(1); % slope is % SOC / time
  end
  Tcharge(i) = time(idx2)-time(idx1); % save time in order to weight averages later
end

% Discharge
for i=1:ndischarge
  % start and end indices of this charge portion
  idx1 = discharge_start(i);
  idx2 = discharge_end(i);
  % fit linear charge rate
  if method == 2 % linear regression forced through 0,0
    X = time(idx1:idx2)(:) - time(idx1); % offset to zero
    Y = cycle_SOC(idx1:idx2)(:) - cycle_SOC(idx1); % offset to zero
    Xdischarge{end+1} = X; Ydischarge{end+1} = Y;
    B = X\Y;
    discharge_rate(i) = B(1); % slope is % SOC / time
  end
  Tdischarge(i) = time(idx2)-time(idx1);
end

%----------------------------------------------------------
% Efficiency

% Calculate intended charge 
nom_charge = nom_charge./rated_cap.*100; % convert to expected % / time
nom_discharge = nom_discharge./rated_cap.*100;
eff_charge = charge_rate./nom_charge;
eff_discharge = discharge_rate./nom_discharge;

% Average efficiency: weight averages by time
w_charge = Tcharge./sum(Tcharge);
avg_charge_eff = sum(w_charge.*eff_charge);
w_discharge = Tdischarge./sum(Tdischarge);
avg_discharge_eff = sum(w_discharge.*eff_discharge);

% Efficiency: calculated charge/discharge rate divided by intended
fprintf('Charge efficiency: %.6f\n', avg_charge_eff)
fprintf('Discharge efficiency: %.6f\n', avg_discharge_eff)

%----------------------------------------------------------
% Residuals (error between linear fit and actual points)

residuals = []; % will be a column vector
xtime = []; % x axis
for i=1:ncharge
  if method == 2 % calculated slope using linear fit through (0,0)
    % charge:
    X = Xcharge{i}; Y = Ycharge{i};
    Yfit = X.*nom_charge(i).*avg_charge_eff; % energy stored = time*rate
    diff = Y - Yfit;
    residuals = [residuals; diff];
    xtime = [xtime; X+time(charge_start(i))];
  end
end
for i=1:ndischarge
  if method == 2 % calculated slope using linear fit through (0,0)
    % discharge:
    X = Xdischarge{i}; Y = Ydischarge{i};
    Yfit = X.*nom_discharge(i).*avg_discharge_eff;
    diff = Yfit - Y; % reverse sign of charge(?)
    residuals = [residuals; diff];
    xtime = [xtime; X+time(discharge_start(i))];
  end
end

% Plot (error between linear fit and actual points)
figure
hold on
plot(xtime,residuals,'o')
title('Residuals')
xlabel('Time (hours)')
ylabel('Residual (total difference in energy stored, Wh)')
hold off
set(gca,'FontSize',20)