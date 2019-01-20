import json
import sys 
from termcolor import colored
from colorama import init
init() #allow coloring on windows


class Error:
    def __init__(self, nb=-1, type = "", line=0, nchar=0, bfile="", stack = "", msg=None):
        if (nb != -1 and type != ""):
            #Exception while throwing the exception -> 6
            #This is a compiler error -> somewhere, an error is badly thrown. Shouldn't occur.
            nb = 6
            type = ""
        
              
        self.message = ""
        if (stack != ""):
            self.message += stack

        if line != 0 and bfile != "":
                target_line = ""
                with open(bfile) as target_file:
                    target_line = target_file.readlines()[line]
                    target_line = target_line.replace(
                        "\t", "").replace("  ", "")
                self.message += "\nIn file %s on line %d, char %d.\n-> %s" % (
                    bfile, line, nchar, target_line)
                self.message += "  " + nchar * " " + "^"

        #add the error info
        with open("data/errors.json") as json_file:
            error_list = json.load(json_file)
        if (nb != -1):
            self.message += colored(error_list["types"][error_list["number"][str(nb)]["type"]] + " " + error_list["number"][str(nb)]["content"],"yellow")
        elif (type != ""):
            if (type in error_list["types"]):
                self.message += colored(error_list["types"][type],"yellow") + " "
            else: 
                #invalid type -> 6
                self.message += error_list["types"]["generic_error"] + " " + error_list["number"]["6"]["content"]
    
        if not msg == None:
                self.message += colored(msg, "yellow")

        


    def launch(self):
        """ Equivalent to a raise. Stops the program and display the error. """
        print("NoKe compiler has encountered an %s.  (︶︿︶)" % colored("error","red"))
        print(self.message)
        sys.exit()  # -> meta break
