% Load .csv file and fill out Cycler text input
% Amps and Ah

clear all

%----------------------------------------------------------

% codes
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

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EDIT THIS INPUT (DEPENDS ON BATTERY/ECM)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% battery info
rated_cap = 1.1; % Ah
max_A = 10;
%nom_A = 30; % multiply normalized input by this
nom_A = 100; % for battery pack

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EDIT THIS INPUT (CYCLE CSV FILE)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% reg 2
outfile = 'StorageCyclerAReg2b.txt';
%outfile = 'StorageCyclerADaily2.txt';
filename = 'reg d regulation signal.csv';
%filename = 'daily_peaker_grid_cycle2.csv';
input = dlmread(filename, ',', 1, 0); % skip first 1 line
time_in = input(:,1);
time_in = time_in - time_in(1); % offset to start at zero
SOC = input(:,2);
charge_rate = nom_A.*SOC./max(SOC); % normalize; scale to max A (works up to nom_A=7.5)

% interpolation (Reg 2)
step = 5; % seconds
time_sec = 0:step:50*60; % up to 50 minutes
charge_A = interp1(time_in.*60,charge_rate,time_sec);
time_sec = step*ones(1,length(charge_A)); % use this 

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
  line = [line, num2str(time_sec(i)), '\t']; % convert time to sec
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