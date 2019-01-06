from enum import Enum
import re


class TypeObject(Enum):
    FUN = 1
    CLASS = 2
    IF = 3
    MODULE = 4
    IMPORT = 5
    VAR = 6


class TypeRun(Enum):
    ASS = 1
    RUNTIME = 2


class NObject:
    def __init__(self, content: str):
        self.childs = []  # Another object like this, lines of a function for example
        self.name = ""  # hello
        self.type = ""  # TypeObject.FUN
        # Let's parse the input string
        # Check if it's a fun|class|module string
        if content.startswith(('fun', 'class', 'module')):
            # It's a fun|class|module
            print("Okay, on allume !")
            # Let's launch the correct regex
            regex = r'(fun|class|module)(?:\s+?[^\S]*)(.+?[^\(|^\ |^\{]*)(?:[\(|\{])'
            match = re.findall(regex, content)
            for test in match:
                self.name = match[0][1]
                self.type = match[0][0]
            if self.type == "fun":
                # Get core of the module between { and }
                childs = content[content.find('{')+1:content.find('}')].split(';')
                childs.pop() # Just remove last element
                print(childs)
                for child in childs:
                    # Each line of code = a child of this NoKeObj
                    self.childs.append(NObject(child))
        else:
            pass
            # Let's launch michel
            print('Martin ? à toi de jouer. Tu vas avoir affaire à une ligne du style "', content, ' "')
            # int michel = 64 par exemple

    def run(self, type: TypeRun):
        if type == TypeRun.ASS:
            pass  # Let's return this object under assembler form
        elif type == TypeRun.RUNTIME:
            pass  # Let's just execute this object
