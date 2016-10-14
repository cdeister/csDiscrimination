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
        end
    end
    sessionMetaData.trialCount=sessionMetaData.trialCount-1;
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
for n=1:sessionMetaData.trialCount
    subplot(2,2,1),hold all
    plot(trialData.states.s5.time{n}(2:end),diff(trialData.states.s5.lickSensor{n}))
    subplot(2,2,2),hold all
    plot(trialData.states.s6.time{n}(2:end),diff(trialData.states.s6.lickSensor{n}))
    subplot(2,2,3),hold all
    plot(trialData.states.s7.time{n}(2:end),diff(trialData.states.s7.lickSensor{n}))
    subplot(2,2,4),hold all
    plot(trialData.states.s8.time{n}(2:end),diff(trialData.states.s8.lickSensor{n}))
end
clear n


%% example analyses (detect licks and lick rates)

% get data
for n=1:sessionMetaData.trialCount
    lsTS_5{n,1}=trialData.states.s5.lickSensor{n};
    lsTS_6{n,1}=trialData.states.s6.lickSensor{n};
    lsTS_7{n,1}=trialData.states.s7.lickSensor{n};
    lsTS_8{n,1}=trialData.states.s8.lickSensor{n};
    lsTV_5{n,1}=trialData.states.s5.time{n};
    lsTV_6{n,1}=trialData.states.s6.time{n};
    lsTV_7{n,1}=trialData.states.s7.time{n};
    lsTV_8{n,1}=trialData.states.s8.time{n};
end

gh=figure(87);
exampleTS=lsTS_5{2};
exampleTV=lsTV_5{2};

%% use amplitude extremes
%
% use and outlier detection algorithm to find putative licks

close all
gh=figure(87);
tsMinMax=[min(exampleTS),max(exampleTS)];
tsDynRange=abs(diff(tsMinMax));
tsMedian=median(exampleTS)
blTS=exampleTS-tsMedian;

% outlier mode
extVals=removeExtremes(exampleTS);
extValLocs=zeros(size(blTS));
extValLocs(extVals)=-2;

% plot stuff
subplot(2,3,1:2)
plot(exampleTV,blTS,'k-')
title(['raw trace; dynRange= ' num2str(tsDynRange)])
hold all
plot(exampleTV(extVals),extValLocs(extVals),'ro')
xlabel('time (sec)')
ylabel('magnitude')


subplot(2,3,3)
nhist(blTS,'box')
xlabel('magnitude')

% extremes lick rate est
ilis=diff(exampleTV(extVals));
lickRates=1./(ilis);
subplot(2,3,6)
nhist(ilis,'box')
xlabel('inter-lick intervals')
subplot(2,3,4:5)
plot(exampleTV(extVals(2:end)),lickRates,'b-')
hold all,plot([0 exampleTV(end)],[median(lickRates) median(lickRates)],'r-')
xlabel('time (sec)')
ylabel('lick rate (Hz)')


%% dynamic range norm'd amplitude threshold
%
% use a simple threshold

ampThr=1.5;
figure(88);
tsMinMax=[min(exampleTS),max(exampleTS)];
tsDynRange=abs(diff(tsMinMax));
tsMedian=median(exampleTS);
blTS=exampleTS-tsMedian;

% threshold mode
% 

% lets use some dynRange delta
% make sure we know the extreme direction
% if the difference between the min and median is positive then
% it is going 

% is the min or the max bigger?
posRange=abs(max(exampleTS)-tsMedian);
negRange=abs(min(exampleTS)-tsMedian);
[~,tMi]=max([negRange,posRange]);

if tMi==1
    % min is bigger
    thrMult=-1;
    minThr=posRange;
    ampThr=((ampThr*minThr)*thrMult);
    extVals=find(blTS<ampThr)-1; % the -1 corrects for deriv shift
elseif tMi==2
    thrMult=1;
    minThr=negRange;
    ampThr=((ampThr*minThr)*thrMult);
    extVals=find(blTS>ampThr); % the -1 corrects for deriv shift
end

extValLocs=zeros(size(blTS));
extValLocs(extVals)=ampThr;  

% plot stuff
subplot(2,3,1:2)
plot(exampleTV,blTS,'k-')
title(['raw trace; dynRange= ' num2str(tsDynRange)])
hold all
plot(exampleTV(extVals),extValLocs(extVals),'ro')
xlabel('time (sec)')
ylabel('magnitude')


subplot(2,3,3)
nhist(blTS,'box')
xlabel('magnitude')

% extremes lick rate est
ilis=diff(exampleTV(extVals));
lickRates=1./(ilis);
subplot(2,3,6)
nhist(ilis,'box')
xlabel('inter-lick intervals')
subplot(2,3,4:5)
plot(exampleTV(extVals(2:end)),lickRates,'b-')
hold all,plot([0 exampleTV(end)],[median(lickRates) median(lickRates)],'r-')
xlabel('time (sec)')
ylabel('lick rate (Hz)')





%%
[tOI,tOV,tNorm,tThrU,tDR,ttt]=drThresh(exampleTS,0);
figure,plot(tNorm,'k-')
hold all,plot([1 numel(exampleTS)],[tThrU tThrU],'r:')
hold all,plot(tOV,'bo')





 