from enum import Enum
import re


class TypeObject(Enum):
    # Type of NoKeObject
    FUN = 1
    CLASS = 2
    IF = 3
    MODULE = 4
    IMPORT = 5
    ASSIGN = 6
    INIT = 7


class TypeRun(Enum):
    # Type of run
    ASS = 1  # Compile to binary
    RUNTIME = 2  # Launch as an interpreted language
    VM = 3  # Compile it to VMed


class NObject:
    def __init__(self, content: str):
        self.children = []  # Another object like this, lines of a function for example
        self.name = ""  # hello
        self.type = ""  # TypeObject.FUN
        self.content = ""  # {bla bla}
        # Let's parse the input string
        # Check if it's a fun|class|module string
        if content.startswith(('fun', 'class', 'module')):
            # It's a fun|class|module
            # Let's launch the regex
            regex = r'(fun|class|module)(?:\s+?[^\S]*)(.+?[^\(|^\ |^\{]*)(?:[\(|\{])'
            match = re.findall(regex, content)
            # Iterate through all found regex group
            for test in match:
                # If all works, we will receive [('type', 'name')]
                self.name = match[0][1]
                type_s = match[0][0]
                if type_s == 'fun':
                    self.type = TypeObject.FUN
                elif type_s == 'class':
                    self.type = TypeObject.CLASS
                elif type_s == 'module':
                    self.type = TypeObject.MODULE
            if self.type == TypeObject.FUN:
                # Get content of the module between { and } and split it
                childs = content[content.find(
                    '{')+1:content.find('}')].split(';')
                childs.pop()  # Just remove last element
                for child in childs:
                    # Each line of code = a child of this NoKeObj
                    self.children.append(NObject(child))
            else:
                # TODO here will be case where type is different than fun
                raise NotImplementedError(
                    'You try to use %s. But it\'s an unimplemented feature' % self.type)
        elif content.startswith('var'):
            # It's the initialization of a variable
            regex = r'(?:var)(?:\s+?[^\S]*)(\S+?[^\s]*)(?:\s+?[^\S]*)(?:\:)(?:\s+?\b)(\S+?[^\s]*)'
            match = re.findall(regex, content)
            self.type = TypeObject.INIT
            for test in match:
                self.name = test[0]  # jean
                self.content = test[1]  # number
        else:
            self.type = 'TODO'
            self.content = content
            self.name = 'TODO'

    def run(self, type_r: TypeRun):
        if type_r == TypeRun.ASS:
            pass  # Let's return this object under assembler form
        elif type_r == TypeRun.RUNTIME:
            pass  # Let's just execute this object
        elif type_r == TypeRun.VM:
            # Let's return this object under VMed form
            # Loop through all children and launch them
            print('Running', self.type, self.name)
            for child in self.children:
                child.run(type_r)
