function [outInd,outVector,normedTS,thrUsed,dynRange,thrType]=drThresh(parseTS,biased,thrVal)

%DRTHRESH   Find crossings over a magnitude within the dynamic range of a time-series.
%   
%   NOTES ON INPUTS (1 2 or 3)
%   "parseTS" is the only required argument and it is a vector that comprise
%   a time-series.
%   
%   This is a seemingly complex function, but it is intended to be simple
%   with advanced use cases. 
%   Reccomended use: "drThresh(parseTS)" and ignore the rest!
%
%   "biased" (boolean; default is 1)
%   This function's default behavior is to determine the skew of your time-series and threshold automatically on
%   the heavy side. So if you have a baseline of 0 and events go mostly above or below. 
%   *** If you chose a biased value you have to also supply a thrValue. 
%   
%   If your events are symetric you should set this to 0 and then it will
%   cut your data in half and work on one side. Which side is determined by
%   your choice of thrVal.
%   
%   "thrVal" (this one is complex)
%   If biased=1 and thrValue is a member of [0 1] then this value is a multiple of the dynamic range, on top
%   of a minimum determined by fluctuations on the non-skewed side of the
%   distribution. For example if you have a time-series whose range is -2
%   and 10 with a median of 0, then the heavy side is 0->10. You would be
%   smart to ignore exursions from 0 to 2 as they are accounted for by
%   noise. So if your thrValue is 0.5 then we choose the threshold to be
%   7 as the range you care about is 0->10. You can override this behavior
%   and use your value with no messing around of it by setting biased to 2 for non-biased hand coded thresh and 3 biased hand-coded threshold.
%   
%
%   NOTES ON OUTPUTS:
%   "outInd" returns the indicies of crossings
%   "outVector" returns a binary vector that is the same size as the parsed
%   time-series that is either 0 (no event) or thrVal (event)
%   "thrUsed" returns the threshold value used 
%   "dynRange" computed range
%   "thrType" 1 if it assumed a value in a normed dist 0->1 and 0 if it
%   used the literal value.
%   "normedTS" returns the median subtracted; dyn range normed time-series
%
%   Reccomended use: drThresh(parseTS); It is designed to just work.
%
%   Chris Deister -- cdeister@brown.edu
%   last rev 10/04/2016



%
% --- resolve args


%determine case based on input
if nargin==1
    thrVal=0.5;
    biased=1;
    parseCase=1; % biased behavior with default threshold [0->1]
    thrType=1;
end

passedThrType=ismember(abs(thrVal),0:0.00001:1);
if nargin==3
    if biased==1 && passedThrType==1
        parseCase=2; % use a 0->1 range threshold on a biased dist.
        thrType=1; % bounded case
    elseif biased ==0 && passedThrType==1
        parseCase=3; % use a 0->1 range threshold on an unbiased dist.
        thrType=1; % bounded case
    elseif biased ==0 && passedThrType==0
        parseCase=7; % use a 0->1 range threshold on an unbiased dist.
        thrType=1; % bounded case
    elseif biased ==1 && passedThrType==0
        parseCase=6; % use a 0->1 range threshold on an unbiased dist.
        thrType=1; % bounded case
    elseif biased ==3
        parseCase=4; % assume literal thresholding on biased 
        thrType=0;
    elseif biased ==2
        parseCase=5; % assume literal thresholding on unbiased
        thrType=0;
    else
        parseCase=8; %???
        disp('i didn''t quite understand the arguments.')
        disp('you could have made a mistake or chris messed up.')
        disp('type doc drThresh and check the arugments or email chris to fix')
    end
end

biasedCases=[1,2,4,6];
unbiasedCases=[3,5,7];


% sort out the time-series
tsMinMax=[min(parseTS),max(parseTS)]
dynRange=abs(diff(tsMinMax));
tsMedian=median(parseTS)
blTS=parseTS-tsMedian;
posRange=abs(max(blTS))
negRange=abs(min(blTS))

if ismember(parseCase,biasedCases)
    [~,tMi]=max([negRange,posRange]);

elseif ismember(parseCase,unbiasedCases)
    if thrVal<0
        tMi=1;
    elseif thrVal>=0
        tMi=2;
    end
end

% clip the relevant portion and flip up (all pos)
normedTS=zeros(size(blTS));
thrUsed=thrVal;

if thrVal<0 % if we got passed a neg threshold flip it for analysis
    thrUsed=thrUsed*-1;
end

if tMi==1
    relValues=find(blTS<0);
    usedRange=negRange;
    opRange=posRange;
elseif tMi==2
    relValues=find(blTS>0);
    usedRange=posRange;
    opRange=negRange;
end
normedTS(relValues)=abs(blTS(relValues));

% normalize distribution if we have a proportional case
if ismember(parseCase,[1,2,3]) % then normalize
    normedTS=normedTS./max(normedTS);
    % NOTE: at this point we have a 0->1 distribution but in cases of 1 and
    % 3 we assume a biased distribution and that we know something about
    % the noise from the data we trashed. So we need to create a min
    % threshold that takes that into account.
    if ismember(parseCase,[1,3])
        minThreshold=opRange./usedRange
    elseif parseCase==2
        minThreshold=0
    end
    if thrUsed<minThreshold
        if parseCase==1
            thrUsed=minThreshold;
        else
            disp('your threshold is below what I think the noise is; you might reconsider')
            disp(['if you do chose something greater than ' num2str(minThreshold)])
        end
    else
    end
end

% this thresholds
outInd=find(normedTS>thrUsed);

outVector=zeros(size(blTS));
outVector(outInd)=thrUsed;  

end

