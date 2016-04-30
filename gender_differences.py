# TODO: add docstring about what this does


import csv
import glob
import itertools
import os
import re

import nltk

from pattern.en import conjugate


# User may have to modify this for their environment.
os.environ["JAVAHOME"] = \
    "/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home"


FILES = glob.iglob("scripts*/**/*.cha")


STEM = nltk.stem.SnowballStemmer("english").stem


PERSON = [1, 2, 3]
TENSE = ["present", "past", "future", "infinitive"]
NUMBER = ["singular", "plural"]
MOOD = ["indicative", "imperative", "conditional", "subjunctive"]
ASPECT = ["imperfective", "perfective", "progressive"]
NEGATED = [True, False]

LIGHT = frozenset(("get", "be", "do", "go", "have"))


# Collects excluded verb forms.
with open("exclusions.txt", "r") as source:
    EXCLUSIONS = frozenset(word.strip().lower() for word in source)


# Collects lexicon.
with open("lexicon.txt", "r") as source:
    LEXICON = frozenset(word.strip().lower() for word in source)


# FIXME(kbg) Add doc strings or at least some explanation for these?


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


def main():
    # TODO: Outside of the loop, create the output directory if it doesn't
    # already exist.
    for fname in FILES:
        # Horribly inefficient but I'll allow it.
        with open(fname, "r") as source:
            fulltext = source.read()
        # TODO: what the heck is this underscore thing about?
        match = re.search("eng\|(.*?)\|CHI\|(.*?)\|(.*?)\|", fulltext)
        if not match:
            continue
        group = match.group(1).replace("_", ",")
        if not group:
            continue
        gender = match.group(2).replace("_", ",")
        if not gender:
            continue
        age = match.group(3).replace("_", ",")
        if not age:
            continue
        match = re.search("@Participants:.*CHI (.*?) ", fulltext)
        if not match:
            continue
        name = match.group(1).replace("_", ",")
        fname = fname.replace("/", ",")
        opath = os.path.join("output",
                             "_".join((name, gender, age, group, fname)) + ".txt")
        if os.path.exists(opath):
            continue
        with open(opath, "w") as sink:
            sink_csv = csv.writer(sink)
            for line in fulltext.split("\n"):
                if not line.startswith("*CHI"):
                    continue
                # TODO: What the heck is this about?
                if line.startswith("*CHI: 0"):
                    continue
                # TODO: Couldn't you just match the non-CHI part instead of
                # rewriting the string? String mutation is horribly
                # inefficient.
                text = re.sub(r"\*CHI:[ \t]", "", line).lower()
                tokens = [t for t in nltk.word_tokenize(text) if
                          re.search("(?=.*\w)^(\w|\")+$", t)]
                verbs = [v for (v, t) in nltk.pos_tag(tokens)
                        if t.startswith("VB")]
                for verb in verbs:
                    stem = STEM(verb).encode("utf8")
                    if verb in EXCLUSIONS:
                        continue
                    if not conjugate(stem, tense="infinitive"):
                        continue
                    if is_no_change(stem):
                        continue
                    if conjugate(stem, tense="infinitive") in LIGHT:
                        continue
                    if not in_vocabulary(conjugate(stem, tense="infinitive")):
                        continue
                    if not conjugate(stem, tense="past").endswith("ed"):
                        continue
                    base = conjugate(stem, tense="infinitive")
                    if is_past_tense_verb(stem, verb):
                        sink_csv.writerow(("PAST", base, verb, verb))
                    elif verb.endswith("ed"):
                        if is_verb(stem, verb):
                            continue
                        if not in_vocabulary(base):
                            continue
                        without_ed = re.search("(.*?)ed", i).group(1)
                        if without_ed.startswith(base):
                            freq_form = conjugate(stem, tense="past")
                        elif is_verb(stem, without_ed):
                            freq_form = without_ed
                        else:
                            freq_form = without_ed[:-1]
                        sink_csv.writerow(("SUSPECT", base, verb, freq_form))


if __name__ == "__main__":
    main()
