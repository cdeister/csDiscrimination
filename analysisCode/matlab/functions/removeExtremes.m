function [badIndicies,goodIndicies,finalThreshold,shaveCounts,numRounds,newData]=removeExtremes(data)

% it always ticks one
numRounds=1;
[tth,tda,tdb]=lowBound(data);

if tdb>0
    while numel(tdb)>0
        shaveCounts(:,numRounds)=numel(tdb);
        [tth,tda,tdb]=lowBound(tda);
        numRounds=numRounds+1;
    end
else
   shaveCounts(:,numRounds)=numel(tdb);
end

finalThreshold=tth;
newData=data(data>=finalThreshold);
badIndicies=find(data<finalThreshold);
goodIndicies=find(data>=finalThreshold);



end