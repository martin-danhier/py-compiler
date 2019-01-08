import json
import sys


class Error:
    def __init__(self, nb: int, line=0, nchar=0 ,bfile="",  stack=[]):
        self.number = nb
        # Open json relative to errors
        with open("data/errors.json") as json_file:
            error_list = json.load(json_file)
        # Build the error message
        self.message = error_list["types"][error_list["number"][str(
            nb)]["type"]] + " " + error_list["number"][str(nb)]["content"]
        # Add info from file and target line
        if line != 0 and bfile != "":
            target_line = ""
            with open(bfile) as target_file:
                target_line = target_file.readlines()[line]
                target_line = target_line.replace("\t", "").replace("  ", "")
            self.message += "\nIn file %s on line %d, char %d.\n-> %s" % (
                bfile, line, nchar, target_line)
            self.message += "  " + nchar*" " + "^"

    def launch(self):
        print("NoKe compiler has encountered an error. (︶︿︶)")
        print(self.message)
        input("Press Ctrl+C to stop, press Enter to continue. But from now on, praying is recommended.\n")

Error(4, 3, 12,"test.idk").launch()