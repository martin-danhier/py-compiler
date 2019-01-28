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

    def __init__(self, file: str):
        # get the text from the file
        source = ""
        if not file[-4:] == '.idk':
            #File is not of the correct file format -> 5
            err = error.Error(5)
            err.launch()
        try:
            # Open and read the file
            with open(file, 'r') as source_file :
                source = source_file.read()
        except:
            # Unable to open file -> 3
            err = error.Error(3)
            err.launch()
        
        
        # Declare the entire file as a module. It will recursively parse into a tree. Like a boss.
        self.main_module = nobject.Module(source,file.strip('.idk'))
        #print(self.main_module)

        # get the regex

        #for match in re.finditer(full_regex, source):
        #    if match.lastgroup == "MISMATCH":
        #        # Regex failed to match -> 1
        #        # <=> SOMEBODY WROTE SHIT INTO THE CODE FILE ITS NOT MY PROBLEM JERRY
        #        err = error.Error(1)
        #        err.launch()
        #        break
        #    # skip those
        #    elif match.lastgroup not in ["SKIP", "COMMENT"] and match.group("DISABLED") == None:
        #        pass

        # objs = source.split("\n\n")  # Separate each module ahaha no
        # for obj in objs:
            # Make all modules one-line
         #   obj = obj.replace("\n", "").replace("\t", "").replace(
          #      "    ", "").replace("        ", "")
            # Create a NoKeObj with this text and add it to the list
           # self.noked_objects.append(nobject.NObject(obj))

    #def run(self):
        # Simply run the program, find the 'main NoKeObject and run it
        #not_found = True
        #i = 0
        # Loop through discovered obj
        #while not_found and i != len(self.noked_objects):
        #    if self.noked_objects[i].name == 'main' and self.noked_objects[i].type == nobject.NObjectNature.FUN:
        #        self.noked_objects[i].run(nobject.NObjectRun.VM)
        #        not_found = False
        #    i += 1
