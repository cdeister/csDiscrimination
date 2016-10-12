% Quick Import and Parsing of CSV Data From Python Discrimination Tasks
%
% cdeister@brown.edu
%
%
%% load csv data
sessionMetaData.filterString='trial';
sessionMetaData.trialCount=1;
sessionMetaData.dataPath=uigetdir();
sessionMetaData.dirObj=dir(sessionMetaData.dataPath);
if numel(numel(sessionMetaData.dirObj)>0)
    for n=1:numel(sessionMetaData.dirObj)
        tempName=sessionMetaData.dirObj(n).name;
        tempBytes=sessionMetaData.dirObj(n).bytes;
        if numel(tempName)>numel(sessionMetaData.filterString)
            if strfind(tempName,sessionMetaData.filterString)>5 && tempBytes>10
                sessionMetaData.trialFiles{sessionMetaData.trialCount,1}=tempName;
                trialData.importData{sessionMetaData.trialCount,1}=...
                    csvread([sessionMetaData.dataPath filesep tempName]);
                sessionMetaData.trialCount=sessionMetaData.trialCount+1;
            end
            sessionMetaData.trialCount=sessionMetaData.trialCount-1;
        end
    end
else
    disp('can''t find data')
end
clear tempName tempBytes n 

%% group data by trials and states
sessionMetaData.dataTypesOrdered=['time','position','state','sensor'];
totalStates=13;
for n=1:numel(trialData.importData)
    for k=1:13
        stateInd=find(trialData.importData{n}(3,:)==k);
        eval(['trialData.states.s' num2str(k) '.time{' num2str(n) '}=trialData.importData{' num2str(n) ...
            '}(1,stateInd);']);
        eval(['trialData.states.s' num2str(k) '.positions{' num2str(n) '}=trialData.importData{' num2str(n) ...
            '}(2,stateInd);']);
        eval(['trialData.states.s' num2str(k) '.states{' num2str(n) '}=trialData.importData{' num2str(n) ...
            '}(3,stateInd);']);
        eval(['trialData.states.s' num2str(k) '.lickSensor{' num2str(n) '}=trialData.importData{' num2str(n) ...
            '}(4,stateInd);']);
        clear stateInd
    end
end

clear k n totalStates

%% This is an example of how to see all lick sensor data (derivs) in states 5,6,7,8
figure
hold all
for n=1:sessionMetaData.trialCount
    subplot(2,2,1)
    plot(trialData.states.s5.time{n}(2:end),diff(trialData.states.s5.lickSensor{n}))
    subplot(2,2,2)
    plot(trialData.states.s6.time{n}(2:end),diff(trialData.states.s6.lickSensor{n}))
    subplot(2,2,3)
    plot(trialData.states.s7.time{n}(2:end),diff(trialData.states.s7.lickSensor{n}))
    subplot(2,2,4)
    plot(trialData.states.s8.time{n}(2:end),diff(trialData.states.s8.lickSensor{n}))
end
clear n

 