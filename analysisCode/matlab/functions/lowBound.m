function [threshold,dataAbove,dataBelow]=lowBound(data)

threshold=median(data)-iqr(data);
dataAbove=data(data>=threshold);
dataBelow=data(data<threshold);


end