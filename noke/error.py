import json
import sys 
from termcolor import colored
from colorama import init
from noke import nobject, tools


def ThrowError(nb=-1,position=None,stack="", msg=None, type=""):
    if (nb != -1 and type != ""):
        #Exception while throwing the exception -> 6
        #This is a compiler error -> somewhere, an error is badly thrown. Shouldn't occur.
        nb = 6
        type = ""
          
    message = ""
    if (stack != ""):
        message += stack
    if position != None:
        coords = tools.get_coords_from_position(position.start, position.file)
        if coords.line != 0 and position.file != "":
            with open(position.file) as target_file:
                temp = tools.custom_strip(target_file.readlines()[coords.line - 1], " ")

            message += 'In File "%s" on line %d, column %d:\n-> %s' % (position.file, coords.line, coords.column, temp[0])
            message += "  " + (coords.column - temp[1]) * " " + "^\n"
    #add the error info
    with open("data/errors.json") as json_file:
        error_list = json.load(json_file)
    if (nb != -1):
        message += colored(error_list["types"][error_list["number"][str(nb)]["type"]] + " " + error_list["number"][str(nb)]["content"],"yellow")
    elif (type != ""):
        if (type in error_list["types"]):
            message += colored(error_list["types"][type],"yellow") + " "
        else: 
            #invalid type -> 6
            message += error_list["types"]["generic_error"] + " " + error_list["number"]["6"]["content"]

    if not msg == None:
            message += colored(msg, "yellow")


    #THROW
    print("NoKe compiler has encountered an %s.  (︶︿︶)" % colored("error","red"))
    print(message)
    sys.exit()  # -> meta break