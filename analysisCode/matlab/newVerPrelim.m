for n=1:10,eval(['aaa_' num2str(n) '=csvread(''/Users/cad/aad_' num2str(n) '.csv'');']),end
for n=1:10,eval(['tbyt_meanDT(:,' num2str(n) ')=mean(diff(aaa_' num2str(n) '(1,:)));']),end
for n=1:10,eval(['tbyt_stdDT(:,' num2str(n) ')=std(diff(aaa_' num2str(n) '(1,:)));']),end
