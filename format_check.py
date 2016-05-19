import glob
import logging
import re
import itertools
import os


FILES = []

for root, directories, filenames in os.walk('scripts/'):
    for filename in filenames: 
        FILES.append(os.path.join(root,filename))

for i in FILES:
    print i
    
logging.basicConfig(level=logging.WARNING)


def main():
    for fname in FILES:
        with open(fname, "r") as source:
            # Horribly inefficient, but we'll allow it.
            filestring = source.read()
            match = re.search("eng\|(.*?)\|CHI\|(.*?)\|(.*?)\|", filestring)
            group = match.group(1) if match else None
                        
            if not group:
                logging.warning("Missing group: %s", fname)
                break
            gender = match.group(2) if match else None
            if not gender:
                logging.warning("Missing gender: %s", fname)
                break
            age = match.group(3) if match else None
            if not age:
                logging.warning("Missing age: %s", fname)
                break
            match = re.search("@Participants:.*CHI (.*?) ", filestring)
            name = match.group(1) if match else None
            if not name:
                logging.warning("Missing name: %s", fname)
                break
                



if __name__ == "__main__":
    main()
