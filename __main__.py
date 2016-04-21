from __future__ import division
import nltk
from pattern.en import conjugate as conjugate_en
from os.path import expanduser
from nltk import tag
import os
import sys
from nltk.stem.porter import *
from nltk.stem.lancaster import *
import glob
import itertools

# Some housekeeping and library loading
reload(sys)
sys.setdefaultencoding('utf-8')
java_path = "/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home"
os.environ['JAVAHOME'] = java_path
home = expanduser("~")
# st = SennaTagger('senna/')
stemmer = LancasterStemmer()

# I know nothing about language so I defined some vars
person = [1,2,3]
tense = ['present','past','future','infinitive']
number = ['singular','plural']
mood = ['indicative','imperative','conditional','subjunctive']
aspect = ['imperfective','perfective','progressive']
negated = [True,False]

with open("exact_exclusion.txt") as word_file:
    exclusions = set(word.strip().lower() for word in word_file)
def is_exclusion(word):
    return word in exclusions

# Check if verb exists (and if its past tense)
def is_past_verb(word,form):
    is_it = any([conjugate_en(word, tense="past", person=p, number=nu, mood=m, aspect=a, negated=n) == form \
    for p in person for nu in number for m in mood for a in aspect for n in negated])
    return is_it
def is_verb(word,form):
    is_it = any([conjugate_en(word, tense=t, person=p, number=nu, mood=m, aspect=a, negated=n) == form \
    for t in tense for p in person for nu in number for m in mood for a in aspect for n in negated])
    return is_it
def is_no_change(word):
    is_it = any([conjugate_en(word, tense="past", person=p, number=nu, mood=m, aspect=a, negated=n) == conjugate_en(word,tense="infinitive")\
    for p in person for nu in number for m in mood for a in aspect for n in negated])
    return is_it

# Check if word is in a big ass collection of English words
with open("wordsEn.txt") as word_file:
    english_words = set(word.strip().lower() for word in word_file)
def is_english_word(word):
    return conjugate_en(word.lower(), tense="infinitive") in english_words

files = itertools.chain.from_iterable(glob.iglob(os.path.join(root,'*.cha'))
 for root, dirs, files in os.walk('scripts/'))

for filename in files:
    with open(filename) as myfile:

        fulltext = open(os.getcwd() + '/' + filename).read()
        match = re.search("eng\|(.*?)\|CHI\|(.*?)\|(.*?)\|", fulltext)
        group = match.group(1) if match else None
        gender = match.group(2) if match else None
        age = match.group(3) if match else None
        match = re.search("@Participants:.*CHI (.*?) ", fulltext);
        name = match.group(1) if match else None
        
        if group and gender and age and name:

            group = re.sub('_', ',', group)
            gender = re.sub('_', ',', gender)
            age = re.sub('_', ',', age)
            name = re.sub('_', ',', name)
            filename = re.sub('/', ',', filename)
            
            if not os.path.exists(os.getcwd() + '/' + 'output/'+name+'_'+gender+'_'+age+'_'+group+'_'+filename+'.txt'):
            
                with open('output/'+name+'_'+gender+'_'+age+'_'+group+'_'+filename+'.txt', "w") as text_file:

                    print('output/'+name+'_'+gender+'_'+age+'_'+group+'_'+filename+'.txt')

                    for line in [l for l in myfile if l.startswith("*CHI") and not l.startswith("*CHI:	0")]:
                        text = re.sub(r'\*CHI:[ \t]', '', line)
                        orig_verbs = nltk.word_tokenize(text.lower())
                        orig_verbs = [t for t in orig_verbs if re.search('(?=.*\w)^(\w|\')+$',t)]
                        stemmed = [stemmer.stem(ste) for ste in orig_verbs]
                        tagged_stems = nltk.pos_tag(orig_verbs)
                        verbs = [(verb, stem) for (verb, stem, tag) in zip(orig_verbs, stemmed, tagged_stems) if tag[1].startswith('VB')]

                        for i,stem in verbs:
                            if conjugate_en(stem, tense="infinitive")\
                               and not is_no_change(stem)\
                               and not conjugate_en(stem, tense="infinitive") == 'get' \
                               and not conjugate_en(stem, tense="infinitive") == 'be' \
                               and not conjugate_en(stem, tense="infinitive") == 'do' \
                               and not conjugate_en(stem, tense="infinitive") == 'go' \
                               and not conjugate_en(stem, tense="infinitive") == 'have' \
                               and is_english_word(conjugate_en(stem, tense="infinitive")) \
                               and not conjugate_en(stem, tense="past").endswith("ed")\
                               and not is_exclusion(i):
                                    
                               if is_past_verb(stem,i):
                                   output = 'PAST,' + conjugate_en(stem, tense="infinitive") + ',' + i + ',' + i + '\n'
                                   text_file.write(output)

                               elif i.endswith('ed') \
                                       and not is_verb(stem, i)\
                                       and is_english_word(conjugate_en(stem, tense="infinitive")):
                                
                                   without_ed = re.search("(.*?)ed", i).group(1)
                                
                                   if without_ed.startswith(conjugate_en(stem, tense="infinitive")):
                                       freq_form = conjugate_en(stem, tense="past")
                                   else:
                                       if is_verb(stem, without_ed):
                                           freq_form = without_ed
                                       else: 
                                           freq_form = without_ed[:-1]
                                
                                   output = 'SUSPECT,' + conjugate_en(stem, tense="infinitive") + ',' + i + ',' + freq_form + '\n'
                                   text_file.write(output)
                                        
                    text_file.close()