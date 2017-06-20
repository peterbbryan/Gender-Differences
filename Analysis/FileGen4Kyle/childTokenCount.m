clear all; close all;

% read in data
[~,~,RAW] = xlsread('spacy_forKyle.xls');

% child names, drop the header row
names = RAW(2:end,2);
% author names, drop the header row
authors = RAW(2:end,1);

% combine the authors and children so I can check for duplicate children
% names
for i = 1:length(names)
    names{i} = strcat(names{i},'_',authors{i});
end

% unique child names
unique_children = unique(names);

% count the number of tokens per child
tokens = nan(size(unique_children));
for i = 1:length(unique_children)
    child_name = unique_children{i};
    tokens(i) = sum(strcmp(child_name,names));
end

% sort and display
temp = [unique_children num2cell(tokens)];
[~,inds] = sort(tokens);
disp(flip(temp(inds,:)));