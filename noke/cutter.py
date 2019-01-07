from noke import error
from noke import nobject


class Cutter:
    def __init__(self, file: str):
        source = ""  # Empty input text for the moment
        try:
            source = open(file, 'r').read()  # Open and read the file
        except:
            err = error.Error(3)  # Unable to open file -> 3
            err.launch()  # Launch the error
        self.noke_obj = []  # All NoKeObject of the program
        objs = source.split("\n\n")  # Separate each module
        for obj in objs:
            # Make all module one-line
            obj = obj.replace("\n", "").replace("\t", "").replace(
                "    ", "").replace("        ", "")
            # Create a NoKeObj with this text and add it to the list
            self.noke_obj.append(nobject.NObject(obj))

    def run(self):
        # Simply run the program, find the 'main NoKeObject and run it
        not_found = True
        i = 0
        # Loop through discovered obj
        while not_found and i != len(self.noke_obj):
            if self.noke_obj[i].name == 'main' and self.noke_obj[i].type == nobject.TypeObject.FUN:
                self.noke_obj[i].run(nobject.TypeRun.VM)
                not_found = False
            i += 1
