clear all; close all;

% column 1: number of tokens female
% column 2: number correct female
% column 3: number overregularized female
% column 4: number of tokens male
% column 5: number correct male
% column 6: number overregularize male
tokens = nan(0,6);

% read in the xls, drop the top row
[~,~,RAW] = xlsread('spacy_forKyle.xls');
names = RAW(1,:);
RAW(1,:) = [];
RAW = cell2table(RAW, 'VariableNames', names);

% half year ranges
for i = 1.5:0.5:5.0
    token_row = nan(1,6);
    age_sample = RAW(RAW.CA > i & RAW.CA <= i+0.5,:);
    
    % female data
    female_sample = age_sample(strcmp('F', age_sample.Sex),:);
    female_sample_correct = female_sample(female_sample.CU == 1,:);
    female_sample_overregularized = female_sample(female_sample.CU == 0,:);
    token_row(:,1) = size(female_sample,1);
    token_row(:,2) = size(female_sample_correct,1);
    token_row(:,3) = size(female_sample_overregularized,1);
    
    % male data
    male_sample = age_sample(strcmp('M', age_sample.Sex),:);
    male_sample_correct = male_sample(male_sample.CU == 1,:);
    male_sample_overregularized = male_sample(male_sample.CU == 0,:);
    token_row(:,4) = size(male_sample,1);
    token_row(:,5) = size(male_sample_correct,1);
    token_row(:,6) = size(male_sample_overregularized,1);
    
    %add to array
    tokens = [tokens; token_row];
end

% disp all
disp(tokens);

% disp female
disp('female');
disp(tokens(:,2)./tokens(:,1));
disp('male');
disp(tokens(:,5)./tokens(:,4));

% disp summary female 
summed = sum(tokens,1);
disp('female');
disp(summed(:,2)./summed(:,1));
disp('male');
disp(summed(:,5)./summed(:,4));
