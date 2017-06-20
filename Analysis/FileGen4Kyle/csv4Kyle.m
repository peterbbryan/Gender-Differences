clear all; close all;

load words;

% sample
% Manchester,Anne,F,1.8525,LOSE,LOST,13974,LOST,TRUE
% 7,4-7,6,5,2,9,10,3,1

% rearranging for Kyle's analysis
output_arr = [words(:,7) words(:,4) words(:,6) words(:,5) words(:,2) words(:,9) words(:,10) words(:,3) words(:,1) words(:,7)];

% replacing, overwriting, capitalizing, etc.
for ind = 1:size(output_arr,1)
    replacement_text = output_arr{ind,2};
    output_arr{ind,2} = replacement_text(1:(length(output_arr{ind,2})-length(output_arr{ind,1})));
    gender = output_arr{ind,3};
    output_arr{ind,3} = upper(gender(1:1));
    if strcmp(output_arr{ind,9},'PAST')
        output_arr{ind,9} = 'TRUE';
    else
        output_arr{ind,9} = 'FALSE';
    end
end

% drop final column
output_arr(:,end) = [];

% write
writetable(cell2table(output_arr, 'VariableNames', {'Corpus','Name','Sex','CA','VB','Target','TargetFreq','Wordform','CU'}), 'spacy_forKyle');