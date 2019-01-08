from noke import error
from noke import nobject
import regex as re
import json

#### DISCLAIMER ####
# This file will be modified.
# It currently hosts the first cutter (module cutter), but module cutter and basic cutter will be merged in the __init__s of NObjects
# This class will then only instanciate the first NObject (file) and run it.


class Cutter:
    # All NoKeObkect's of the program
    noked_objects: list

    def __init__(self, file: str):
        # get the text from the file
        source = ""
        try:
            # Open and read the file
            source = open(file, 'r').read()
        except:
            # Unable to open file -> 3
            err = error.Error(3)
            err.launch()

        # get the regex
        with open('data/cutter_rules.json', 'r') as json_file:
            rules = json.load(json_file)
        full_regex = "|".join("(?P<%s>%s)" % (
            rule, rules[rule]) for rule in rules)
        for match in re.finditer(full_regex, source):
            if match.lastgroup == "MISMATCH":
                # Regex failed to match -> 1
                # <=> SOMEBODY WROTE SHIT INTO THE CODE FILE ITS NOT MY PROBLEM JERRY
                err = error.Error(1)
                err.launch()
                break
            # skip those
            elif match.lastgroup not in ["SKIP", "COMMENT"] and match.group("DISABLED") == None:
                pass

        # objs = source.split("\n\n")  # Separate each module ahaha no
        # for obj in objs:
            # Make all modules one-line
         #   obj = obj.replace("\n", "").replace("\t", "").replace(
          #      "    ", "").replace("        ", "")
            # Create a NoKeObj with this text and add it to the list
           # self.noked_objects.append(nobject.NObject(obj))

    def run(self):
        # Simply run the program, find the 'main NoKeObject and run it
        not_found = True
        i = 0
        # Loop through discovered obj
        while not_found and i != len(self.noked_objects):
            if self.noked_objects[i].name == 'main' and self.noked_objects[i].type == nobject.NObjectNature.FUN:
                self.noked_objects[i].run(nobject.NObjectRun.VM)
                not_found = False
            i += 1
