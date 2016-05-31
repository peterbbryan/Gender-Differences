#!/usr/bin/python

import csv
import glob
import itertools
import os
import re
import nltk
from pattern.en import conjugate
import spacy
import sys
import logging

FILES = []
for root, directories, filenames in os.walk('scripts/'):
	for filename in filenames: 
		FILES.append(os.path.join(root,filename))

logging.basicConfig(level=logging.INFO)

TAGGER = sys.argv[1]

if (TAGGER == "senna"):
	os.environ["JAVAHOME"] = \
	"/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home"
	TAG = SennaTagger('senna/')
elif (TAGGER == "nltk"):
	TAG = nltk.pos_tag
elif (TAGGER == "spacy"):
	TAG = spacy.load('en')
elif (TAGGER == ''):
	logging.warning("No tagger specified. Defaulting to NLTK")
	TAG = nltk.pos_tag
else:
	logging.error("Unknown stemmer: %s", TAGGER)

SAVE_PATH = "output_" + TAGGER
STEM = nltk.stem.SnowballStemmer("english").stem

PERSON = [1, 2, 3]
TENSE = ["present", "past", "future", "infinitive"]
NUMBER = ["singular", "plural"]
MOOD = ["indicative", "imperative", "conditional", "subjunctive"]
ASPECT = ["imperfective", "perfective", "progressive"]
NEGATED = [True, False]

AUTHORS = ['Thomas','Kuczaj','Brown','Macwhinney','Lara','Macwhinney', \
	'Brown','Providence','Manchester','Suppes','Manchester','Providence','Bloom70','Bloom73',\
	'Manchester','Manchester','Manchester','Manchester','Sachs','Manchester', \
	'Braunwald','Manchester','Clark','Providence','Manchester','Manchester', \
	'Manchester','Brown','Snow','Providence','Providence','Manchester','Demetras1', \
	'Providence','Hall','Hall','Hall','Hall','Hall','Hall','Hall','Hall','Hall', \
	'Hall','Hall','Hall','Hall','Bloom73','Hall','Bohannan','Higginson']
AUTHORS = [author.lower() for author in AUTHORS]
	
CHILDREN = ['Thomas','Abe','Adam','Ross','Lara','Mark','Sarah','Naima','Aran', \
	'Nina','Anne','Lily','Peter','Carl','Joel','Dominic','Gail','Naomi','Becky', \
	'Laura','Liz','Shem','Ethan','Ruth','Warren','John','Eve','Nathaniel','William', \
	'Violet','Nicole','Trevor','Alex','Tony','Chris','Tracy','Brett','Gabriella', \
	'Kip','Matthew','Bobby','Zoe','Julia','Joey','Mim','Dexter','Allison', \
	'Anthony','Nathaniel','April']
CHILDREN = [child.lower() for child in CHILDREN]

LIGHT = frozenset(("get", "be", "do", "go", "have"))

NLP = spacy.load('en')

# Collects excluded verb forms.
with open("exclusions.txt", "r") as source:
	EXCLUSIONS = frozenset(word.strip().lower() for word in source)

# Collects lexicon.
with open("lexicon.txt", "r") as source:
	LEXICON = frozenset(word.strip().lower() for word in source)

def is_past_tense_verb(word, form):
	return any(conjugate(word, tense="past", person=p, number=nu, mood=m,
		aspect=a, negated=n) == form for p in PERSON for nu in NUMBER for m in
		MOOD for a in ASPECT for n in NEGATED)

def is_verb(word, form):
	return any(conjugate(word, tense=t, person=p, number=nu, mood=m, aspect=a,
		negated=n) == form for t in TENSE for p in PERSON for nu in NUMBER
		for m in MOOD for a in ASPECT for n in NEGATED)

def is_no_change(word):
	return any(conjugate(word, tense="past", person=p, number=nu, mood=m,
		aspect=a, negated=n) == conjugate(word, tense="infinitive") for p in
		PERSON for nu in NUMBER for m in MOOD for a in ASPECT for n in NEGATED)

def in_vocabulary(word):
	return conjugate(word.lower(), tense="infinitive") in LEXICON


def verb_extract(child_speech):
	tokenized = [nltk.word_tokenize(line) for line in child_speech]  
	tokenized = list(itertools.chain.from_iterable(tokenized))
	tokens = [token for token in tokenized if re.match("^[A-Za-z.]*$",token)]
	verbs = []
	if TAGGER == "senna" or TAGGER == "nltk":
		tokens = ' '.join(tokens).split('.')
		tagged = [[verb.lower() for (verb,POS) in liste if POS.startswith('VB')] for \
		liste in [nltk.pos_tag(nltk.word_tokenize(token)) for token in tokens]]
		verbs = [item for sublist in verbs for item in sublist]	
	elif TAGGER == "spacy":
		tokens = ' '.join(tokens)
		tokens = NLP(unicode(tokens), entity=False)
		tokens = zip(tokens,[str(tok.tag_) for tok in tokens])
		verbs = [str(verb).lower() for (verb,pos) in tokens if pos.startswith('VB')]        
	verbs = filter(None, verbs)    
	verbs = [(verb, STEM(verb).encode("utf8")) for verb in verbs]
	verbs = [(verb,stem) for (verb,stem) in verbs if not (verb in EXCLUSIONS or \
		not conjugate(stem, tense="infinitive") or \
		is_no_change(stem) or \
		conjugate(stem, tense="infinitive") in LIGHT or \
		not in_vocabulary(conjugate(stem, tense="infinitive")) or \
		conjugate(stem, tense="past").endswith("ed"))]
	return verbs


def main():
	# TODO: Outside of the loop, create the output directory if it doesn't
	# already exist.
	if os.path.exists(SAVE_PATH):
		logging.warning("Output folder detected. Only new .cha input files will be added")
	else:
		os.makedirs(SAVE_PATH)
	
	for fname in FILES:
		logging.info("Processing: " + fname)

		with open(fname, "r") as source:
			fulltext = source.read()

		match = re.search("eng\|(.*?)\|CHI\|(.*?)\|(.*?)\|", fulltext)
		if not match:
			continue
		group = match.group(1).replace("_", ",")
		gender = match.group(2).replace("_", ",")
		age = match.group(3).replace("_", ",")
		part = re.search("@Participants:.*CHI (.*?) ", fulltext)

		if not (match and group and gender and age and part):
			continue
	   
		name = part.group(1).replace("_", ",")
		fname = fname.replace("/", ",")
		opath = os.path.join(SAVE_PATH,
							 "_".join((name, gender, age, group, fname)) + ".txt")

		if not (name.lower() in CHILDREN and group.lower() in AUTHORS):
			continue

		if os.path.exists(opath):
		   continue
			
		with open(opath, "w") as sink:
			sink_csv = csv.writer(sink, delimiter = ',')
				
			lines = [line for line in fulltext.decode('utf-8').split("\n")]            
			child_speech = [m.group(1) for m in (re.search(r"\*CHI:(.*)", l) for l in lines) if m]    
			
			verbs = verb_extract(child_speech)
			
			rows = []
			
			for (verb,stem) in verbs:
				
				base = conjugate(stem, tense="infinitive")
				if is_past_tense_verb(stem, verb):
					rows.append(["PAST", base, verb, verb])
				
				elif verb.endswith("ed"):
					
					if is_verb(stem, verb):
						continue
					if not in_vocabulary(base):
						continue
					
					if verb.startswith(base):
						freq_form = conjugate(stem, tense="past")
					elif verb.startswith(conjugate(stem, tense="past")):
						freq_form = conjugate(stem, tense="past")
					elif verb.startswith(conjugate(stem, tense="pastparticiple")):
						freq_form = conjugate(stem, tense="pastparticiple")
					else:
						print(base)
					
					rows.append(["SUSPECT", base, verb, freq_form])
				   
			sink_csv.writerows(rows)

if __name__ == "__main__":
	main()

