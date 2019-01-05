import json, sys

class Error:
    def __init__(self, nb : int):
        self.number = nb
        # Open json relative to errors
        with open("data/errors.json") as json_file:
            error_list = json.load(json_file)
        # Build the error message
        self.message = error_list["types"][error_list["number"][str(nb)]["type"]] + " " + error_list["number"][str(nb)]["content"]
    def launch(self):
        print("NoKe compiler has encountered an error. (︶︿︶)")
        print(self.message)
        input("Press Ctrl+C to stop enter to continue. But from now on, praying is recommended.")

error = Error(3)
error.launch()
