clear all; close all;

files = dir('output_spacy/*.txt');
filenames = {files.name};

% read from the files and split the data into an array
words = cell(0,9);
for val = filenames
    name_parts = strsplit(val{:},'_');
        
    if length(name_parts) ~= 5; continue; end;
    data = importdata(['output_spacy/' val{:}])';
    for i = data
        words = [words; [strsplit(i{:},',') name_parts]];
    end
end

% sloppy move on a column 
words = [words words(:,4)];
words(:,4) = [];

% calculate ages
age = nan(size(words(:,5)));
for i = 1:length(age)
    name_parts = strsplit(words{i,5},';');
    years = str2num(name_parts{1});
    
    if(isempty(name_parts{2}))
        months = 0;
        days = 15.218;
    else
        name_parts2 = strsplit(name_parts{2},'.');
        months = str2num(name_parts2{1});
        days = str2num(name_parts2{2});
        if isempty(months); months = 0; end;
        if isempty(days); days = 15.218; end;
    end
        
    if isempty(months); months = 6; end;
    if isempty(days); days = 15.218; end;
    
    age(i) = (years) + ((months + (days/(365.25/12)))/12);
end

% filter out excluded ages
words(age < 1.5 | age > 5.5,:) = [];
age(age < 1.5 | age > 5.5,:) = [];

% names
names = lower({'Thomas','Abe','Adam','Ross','Lara','Mark','Sarah','Naima','Aran', ... 
    'Nina','Anne','Lily','Peter','Carl','Joel','Dominic','Gail','Naomi','Becky', ...
    'Laura','Liz','Shem','Ethan','Ruth','Warren','John','Eve','Nathaniel','William', ...
    'Violet','Nicole','Trevor','Alex','Tony','Chris','Tracy','Brett','Gabriella', ...
    'Kip','Matthew','Bobby','Zoe','Julia','Joey','Mim','Dexter','Allison', ...
    'Anthony','Nathaniel','April'});
research_groups = lower({'Thomas','Kuczaj','Brown','Macwhinney','Lara','Macwhinney', ...
    'Brown','Providence','Manchester','Suppes','Manchester','Providence','Bloom70', ...
    'Manchester','Manchester','Manchester','Manchester','Sachs','Manchester', ...
    'Braunwald','Manchester','Clark','Providence','Manchester','Manchester', ...
    'Manchester','Brown','Snow','Providence','Providence','Manchester','Demetras1', ...
    'Providence','Hall','Hall','Hall','Hall','Hall','Hall','Hall','Hall','Hall', ...
    'Hall','Hall','Hall','Hall','Bloom73','Hall','Bohannon','Higginson'});

% every to lower case
words(:,2:4) = lower(words(:,2:4));
words(:,7) = lower(words(:,7));

% mark words that shouldn't be included
word_remove = zeros(size(words,1),1);
for i = 1:size(words,1)
    name = words{i,4};
    group = words{i,7};

    if ~any(strcmp(name,names) + strcmp(group,research_groups) == 2)
        word_remove(i) = 1;
    end
    
    % a bit of combination
    words{i,4} = [name group];
end

% store the words before we toss the garbage, should be empty-ish
store = words(find(word_remove),:);

% clean out the trash
words(find(word_remove),:) = [];
age(find(word_remove)) = [];

% let's add some word frequencies
[~,~,word_freq] = xlsread('SUBTLEXusExcel2007.xlsx');

% find the frequencies in the 2nd column of the SUBTLEX table
frequencies = nan(size(words,1),1);
words(:,5) = num2cell(age);
for word = 1:size(words,1)
    freq_row = word_freq(strcmpi(words(word,9),word_freq(:,1)),:);
    if ~isempty(freq_row)
        frequency = freq_row{:,2};
    else
        frequency = 0;
    end
    frequencies(word) = frequency;
end

% add a column on frequencies
words = [words num2cell(frequencies)];

% 1 character verbs would be pretty bad....
lengths = cellfun(@(x) numel(x), words(:,3));
words(lengths <= 1,:) = [];

% save all that fine data
save words;
writetable(cell2table(words,'VariableNames',{'TENSE','ROOT','FORM','NAME_AND_AUTHOR','AGE','GENDER','AUTHOR','PATH','REALPAST','FREQUENCY'}),'table.csv');
