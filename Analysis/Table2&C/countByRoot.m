clear all; close all;

% read in the xls, drop the top row
[~,~,RAW] = xlsread('spacy_forKyle.xls');
names = RAW(1,:);
RAW(1,:) = [];
RAW = cell2table(RAW, 'VariableNames', names);

% just the unique words
unique_words = unique(RAW.VB);

% column 1: verb root
% column 2: female correct count
% column 3: female overregularization count
% column 4: male correct count
% column 5: male overregularization count
output_table = cell(0,5);

for i = unique_words'

    % row for the output table
    row = cell(1,5);
    
    % sample of word specific rows
    word_sample = RAW(strcmp(i, RAW.VB),:);
    
    % female data
    female_sample = word_sample(strcmp('F', word_sample.Sex),:);
    female_sample_correct = female_sample(female_sample.CU == 1,:);
    female_sample_overregularized = female_sample(female_sample.CU == 0,:);
    
    % male data
    male_sample = word_sample(strcmp('M', word_sample.Sex),:);
    male_sample_correct = male_sample(male_sample.CU == 1,:);
    male_sample_overregularized = male_sample(male_sample.CU == 0,:);
    
    % output row
    row{1,1} = i;
    row{1,2} = size(female_sample_correct,1);
    row{1,3} = size(female_sample_overregularized,1);
    row{1,4} = size(male_sample_correct,1);
    row{1,5} = size(male_sample_overregularized,1);
    
    output_table = [output_table; row];
end

% disp all
output_table = cell2table(output_table, 'VariableNames', {'VB','FemaleCorrectCount', ...
    'FemaleOverregularizationCount','MaleCorrectCount','MaleOverregularizationCount'});
disp(output_table);
writetable(output_table, 'verb_counts.xls');
