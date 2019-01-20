import json
import sys


class Error:
    def __init__(self, nb=-1, line=0, nchar=0 , bfile="", stack=[], msg=None):
        if not nb == -1:
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
            if not msg == None:
                self.message += "\n" + msg
        else:
            self.message = msg

    def launch(self):
        """ Equivalent to a raise. Stops the program and display the error. """
        print("NoKe compiler has encountered an error. (︶︿︶)")
        print(self.message)
        sys.exit() # -> meta break

Error(1, msg="yo").launch()