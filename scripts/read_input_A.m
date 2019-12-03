% Load .csv file and fill out Cycler text input
% Amps and Ah

clear all

%----------------------------------------------------------

% BDS cycle codes
charge = '1';
rest = '3';
discharge = '2';
power = '3';
current = '1';
time = '3';

% fixed pieces of Cycler input
part1 = 'Cycler\nVersion_1\n';
endsim = '4\t0\t1\t0\t10\t0\t10\t0.1\t60\t25\t0\n';
part2 = 'Oven\nDisabled\n0\nHTC	=	         100\nOVEN CONVECTION MODE	=	0\nFilter	=	\nInitTemp	=	25';

%----------------------------------------------------------
% EDIT THIS INPUT (DEPENDS ON BATTERY/ECM)
%----------------------------------------------------------
% battery info
%nom_Ah = 7; % Ah
max_A = 10; % max A of 18650 battery
%nom_A = 30; % A (multiply normalized input by this)
nom_A = 100; % for battery pack
%nom_A = 1.5;

%----------------------------------------------------------
% EDIT THIS INPUT (CYCLE CSV FILE)
%----------------------------------------------------------

% read input (Reg 1)
outfile = 'StorageCyclerAReg1b.txt';
filename = 'regd-test-wave - Copy.csv';
input = dlmread(filename, ',', 2, 0); % skip first 2 lines
time_sec = input(:,2);
SOC = input(:,3); % normalized power
charge_A = SOC.*nom_A; % convert to A

% read input (Daily 1)
##outfile = 'StorageCyclerADaily1.txt';
##filename = 'daily_peaker_profile.csv';
##input = dlmread(filename, ',', 1, 0); % skip first 1 line
##time_hr = input(2:end,1); % skip first time
##SOC = nom_Ah.*input(:,2)./100; % total SOC in Ah
##charge_Ah = diff(SOC); % how much ADDED charge each time period
##charge_A = charge_Ah./time_hr; % charge rate over each time period
##time_sec = time_hr.*3600;

%----------------------------------------------------------

% assemble text
sim = '';
for i=1:length(time_sec)
  line = '';
  if charge_A(i)>0
    line = [line, charge, '\t'];
  else
    line = [line, discharge, '\t']; % discharge
    charge_A(i) = abs(charge_A(i));
  end
  line = [line, current, '\t']; % THIS LINE CHANGED WHEN CHARGING BY CURRENT V. POWER
  line = [line, num2str(charge_A(i)), '\t'];
  line = [line, time, '\t'];
  line = [line, num2str(time_sec(i)), '\t'];
  line = [line, '0\t0\t0.1\t60\t0\t0\n'];
  sim = [sim, line];
end

nlines = [num2str(length(time_sec)+1),'\n'];

text = [part1, nlines, sim, endsim, part2];
%fprintf(text)
fprintf('number of lines:\n%d\n',length(time_sec)+1)

%----------------------------------------------------------

% write to file
fileID = fopen(outfile,'w');
fprintf(fileID,[part1,nlines,sim,endsim,part2]);
fclose(fileID);