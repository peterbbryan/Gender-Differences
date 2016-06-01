#!/usr/bin/python

import csv
import glob
import itertools
import os
import re
import nltk
import spacy
import sys, getopt
import logging
from pattern.en import conjugate

# Setup
logging.basicConfig(level=logging.INFO)
STEM = nltk.stem.SnowballStemmer("english").stem
SCRIPT_DIRECTORY = ""
OUTPUT_DIRECTORY = ""
TAGGER = ""
TAG = []

# Pattern language arguments
PERSON = [1, 2, 3]
TENSE = ["present", "past", "future", "infinitive"]
NUMBER = ["singular", "plural"]
MOOD = ["indicative", "imperative", "conditional", "subjunctive"]
ASPECT = ["imperfective", "perfective", "progressive"]
NEGATED = [True, False]

# Authors included in the CHILDES database
AUTHORS = ['Thomas','Kuczaj','Brown','Macwhinney','Lara','Macwhinney', \
	'Brown','Providence','Manchester','Suppes','Manchester','Providence','Bloom70','Bloom73',\
	'Manchester','Manchester','Manchester','Manchester','Sachs','Manchester', \
	'Braunwald','Manchester','Clark','Providence','Manchester','Manchester', \
	'Manchester','Brown','Snow','Providence','Providence','Manchester','Demetras1', \
	'Providence','Hall','Hall','Hall','Hall','Hall','Hall','Hall','Hall','Hall', \
	'Hall','Hall','Hall','Hall','Bloom73','Hall','Bohannan','Higginson']
AUTHORS = [author.lower() for author in AUTHORS]

# Children included in the CHILDES database
CHILDREN = ['Thomas','Abe','Adam','Ross','Lara','Mark','Sarah','Naima','Aran', \
	'Nina','Anne','Lily','Peter','Carl','Joel','Dominic','Gail','Naomi','Becky', \
	'Laura','Liz','Shem','Ethan','Ruth','Warren','John','Eve','Nathaniel','William', \
	'Violet','Nicole','Trevor','Alex','Tony','Chris','Tracy','Brett','Gabriella', \
	'Kip','Matthew','Bobby','Zoe','Julia','Joey','Mim','Dexter','Allison', \
	'Anthony','Nathaniel','April']
CHILDREN = [child.lower() for child in CHILDREN]

# Excluded light verb stems
LIGHT = frozenset(("get", "be", "do", "go", "have"))

# Collects excluded verb forms
with open("exclusions.txt", "r") as source:
	EXCLUSIONS = frozenset(word.strip().lower() for word in source)

# Collects lexicon
with open("lexicon.txt", "r") as source:
	LEXICON = frozenset(word.strip().lower() for word in source)

# Check if given form is a correct tense conjugation of a given verb stem
def is_verb(word, form, tenses=TENSE):
	return any(conjugate(word, tense=t, person=p, number=nu, mood=m, aspect=a,
		negated=n) == form for t in tenses for p in PERSON for nu in NUMBER
		for m in MOOD for a in ASPECT for n in NEGATED)

# Check if the past tense of a word is the same as its infinitive form
def is_no_change(word):
	return any(conjugate(word, tense="past", person=p, number=nu, mood=m,
		aspect=a, negated=n) == conjugate(word, tense="infinitive") for p in
		PERSON for nu in NUMBER for m in MOOD for a in ASPECT for n in NEGATED)

# Check if word is in a large corpus of English words
def in_vocabulary(word):
	return conjugate(word.lower(), tense="infinitive") in LEXICON

# Apply verb extraction method specific to the selected tagger
def verb_extract(child_speech):
	tokenized = [nltk.word_tokenize(line) for line in child_speech]  
	tokenized = list(itertools.chain.from_iterable(tokenized))
	tokens = [token for token in tokenized if re.match("^[A-Za-z.]*$", token)]
	verbs = []
	if TAGGER == "senna" or TAGGER == "nltk":
		tokens = ' '.join(tokens).split('.')
		tagged = [[verb.lower() for (verb,POS) in liste if POS.startswith('VB')] for \
		liste in [nltk.pos_tag(nltk.word_tokenize(token)) for token in tokens]]
		verbs = filter(None, tagged)    
		verbs = [item for sublist in verbs for item in sublist]	
	elif TAGGER == "spacy":
		tokens = ' '.join(tokens)
		tokens = TAG(unicode(tokens), entity=False)
		tokens = zip(tokens, [str(tok.tag_) for tok in tokens])
		verbs = [str(verb).lower() for (verb, pos) in tokens if pos.startswith('VB')]        
	verbs = [(verb, STEM(verb).encode("utf8")) for verb in verbs]
	verbs = [(verb, stem) for (verb, stem) in verbs if not (verb in EXCLUSIONS or \
		not conjugate(stem, tense="infinitive") or \
		is_no_change(stem) or \
		conjugate(stem, tense="infinitive") in LIGHT or \
		not in_vocabulary(conjugate(stem, tense="infinitive")) or \
		conjugate(stem, tense="past").endswith("ed"))]
	return verbs
	
# Identify correct past tense and overregularized tokens and print to CSV
def main(argv):
	global TAGGER, SCRIPT_DIRECTORY, OUTPUT_DIRECTORY, TAG
	OVERWRITE = 0
	
	try:
		opts, args = getopt.getopt(argv,"hs:t:o:",["scriptdir=","tagger=","outputdir"])
	except getopt.GetoptError:
		logging.DEBUG('gender_differences.py -s <scriptdir> -t <tagger> -o <outputdir> -x <overwrite>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			logging.DEBUG('gender_differences.py -s <scriptdir> -t <tagger> -o <outputdir> -x <overwrite>')
			sys.exit()
		elif opt in ("-s", "--scriptdir"):
			SCRIPT_DIRECTORY = arg
		elif opt in ("-t", "--tagger"):
			TAGGER = arg
		elif opt in ("-x", "--overwrite"):
			OVERWRITE = arg
		elif opt in ("-o", "--outputdir"):
			OUTPUT_DIRECTORY = arg
			
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
		TAGGER = "nltk"
		TAG = nltk.pos_tag
	else:
		logging.error("Unknown stemmer: " + TAGGER + ". Choose 'nltk' (default), 'spacy', or 'senna'")
		sys.exit(1)
		
	if not SCRIPT_DIRECTORY:
		SCRIPT_DIRECTORY = "scripts"
		logging.warning("No script directory specified. Defaulting to scripts")
	if not OUTPUT_DIRECTORY:
		OUTPUT_DIRECTORY = "output_" + TAGGER
		logging.warning("No output directory specified. Defaulting to output_" + TAGGER)

	FILES = []
	for root, directories, filenames in os.walk(SCRIPT_DIRECTORY):
		for filename in filenames: 
			FILES.append(os.path.join(root,filename))
		
	if os.path.exists(OUTPUT_DIRECTORY):
		logging.warning("Output folder detected")
		if OVERWRITE: 
			logging.warning("Existing files will be overwritten")
		
	else:
		os.makedirs(OUTPUT_DIRECTORY)
	
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
		opath = os.path.join(OUTPUT_DIRECTORY,
							 "_".join((name, gender, age, group, fname)) + ".txt")

		if not (name.lower() in CHILDREN and group.lower() in AUTHORS):
			continue
		if os.path.exists(opath):
			if not OVERWRITE:
				continue
			
		with open(opath, "w") as sink:
			sink_csv = csv.writer(sink, delimiter = ',')
				
			lines = [line for line in fulltext.decode('utf-8').split("\n")]            
			child_speech = [m.group(1) for m in (re.search(r"\*CHI:(.*)", l) for l in lines) if m]    
			
			verbs = verb_extract(child_speech)
			
			rows = []
			
			for (verb, stem) in verbs:
				base = conjugate(stem, tense="infinitive")
				
				if is_verb(stem, verb ,"past"):
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
					rows.append(["SUSPECT", base, verb, freq_form])
				   
			sink_csv.writerows(rows)

if __name__ == "__main__":
	main(sys.argv[1:])
