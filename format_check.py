from __future__ import division
import nltk
from pattern.en import conjugate as conjugate_en
from os.path import expanduser
from nltk.tag.senna import SennaTagger
import os
import sys
from nltk.stem.porter import *
import glob
import itertools


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
		
		if not (group and gender and age and name):
			print filename

			