from enum import Enum
import re


class NObjectNature(Enum):
    # Type of NObject. Problem : it is possible to declare a LOOP as a CLASS :/ kind of "dirty" method then
    FILE = 0
    MODULE = 1
    FUN = 2
    CLASS = 3
    CONDITION = 4
    LOOP = 5
    WHILE_LOOP = 6
    FOR_LOOP = 7
    INSTRUCTION = 8
    IMPORT = 9
    ASSIGNEMENT = 10
    CALL = 11
    OPERATION = 12
    INSTANCIATION = 13


class NObjectRun(Enum):
    # Type of run
    ASS = 1  # Compile to binary
    VM = 2  # Compile it to VMed


class NObject:
    """ The base class. """
    parent : object
    children : list


    def __init__(self, body: str, parent = None):
        """ Create a NObject. 
        Parameters
        ----------
        nature : the type of the NObject (NObjectNature)
        body : the body of the NObject (str)
        parent : the NObject of which this one is the children. Leave it to None."""
        self.parent = parent
        # process body

    def get_stack_trace(self):
        """ Get a stacktrace from this NObject. 
        Returns
        -------
        stack_trace : a str that countains many infos to find this NObject again in the code"""

        stack_trace = '\nin File: "%s" in %s. Details TODO' % ('<file. TODO>', self.__class__.__name__)
        if self.parent != None:
            stack_trace += self.parent.get_stack_trace()
        return stack_trace

class Module(NObject):
    """ A module is a set of other modules, like fun or Classes.
    => init must check that children are exclusively modules"""
    identifier: str  # the name of the module

    def __init__(self, nature: NObjectNature, body: str, identifier: str):
        NObject.__init__(self, nature, body)
        self.identifier = identifier


class Fun(Module):
    """A function is... a function.
    => init must analyse the parameters
    """
    return_type: str
    parameters: list

    def __init__(self, nature: NObjectNature, body: str, identifier: str, parameters: str, return_type: str):
        Module.__init__(self, nature, body, identifier)
        self.return_type = return_type
        # process parameters


class Class(Module):
    # todo
    pass


class Condition(NObject):
    """ ex:"if (x > 2) { thing } else {}" is a Conditional instruction
        it has the particulary to have 2 children : if and else (else ifs are just ifs in the else of another if)
        if there is no else statement, else_condition and else_children are None and are skipped when the condition is false
       """
    condition: list  # to revise
    else_condition: list  # to revise too
    else_children: []


class Loop(NObject):
    # to think then do
    pass


class Instruction(NObject):
    """ex: "int a = 2" is an instruction of type "assignement".
    the left part (int a) is an instruction of type "instanciation".
    the right part (2) is also an instanciation."""
    instruction_type: object  # maybe create an enum with the type ? Or use NObjectNature ?
    pass


# WORK IN PROGRESS


# class NObject:
#    children : list
#    name : str
#    type : TypeObject
#
#    def __init__(self, content: str):
#        self.children = []  # Another object like this, lines of a function for example
#        self.name = ""  # hello
#        self.type = ""  # TypeObject.FUN
#        self.content = ""  # {bla bla}
#        # Let's parse the input string
#        # Check if it's a fun|class|module string
#        if content.startswith(('fun', 'class', 'module')):
#            # It's a fun|class|module
#            # Let's launch the regex
#            regex = r'(fun|class|module)(?:\s+?[^\S]*)(.+?[^\(|^\ |^\{]*)(?:[\(|\{])'
#            match = re.findall(regex, content)
#            # Iterate through all found regex group
#            for test in match:
#                # If all works, we will receive [('type', 'name')]
#                self.name = match[0][1]
#                type_s = match[0][0]
#                if type_s == 'fun':
#                    self.type = TypeObject.FUN
#                elif type_s == 'class':
#                    self.type = TypeObject.CLASS
#                elif type_s == 'module':
#                    self.type = TypeObject.MODULE
#            if self.type == TypeObject.FUN:
#                # Get content of the module between { and } and split it
#                childs = content[content.find(
#                    '{')+1:content.find('}')].split(';')
#                childs.pop()  # Just remove last element
#                for child in childs:
#                    # Each line of code = a child of this NoKeObj
#                    self.children.append(NObject(child))
#            else:
#                # TODO here will be case where type is different than fun
#                raise NotImplementedError(
#                    'You try to use %s. But it\'s an unimplemented feature' % self.type)
#        elif content.startswith('var'):
#            # It's the initialization of a variable
#            regex = r'(?:var)(?:\s+?[^\S]*)(\S+?[^\s]*)(?:\s+?[^\S]*)(?:\:)(?:\s+?\b)(\S+?[^\s]*)'
#            match = re.findall(regex, content)
#            self.type = TypeObject.INIT
#            for test in match:
#                self.name = test[0]  # jean
#                self.content = test[1]  # number
#        else:
#            self.type = 'TODO'
#            self.content = content
#            self.name = 'TODO'
#
#    def run(self, type_r: TypeRun):
#        if type_r == TypeRun.ASS:
#            pass  # Let's return this object under assembler form
#        elif type_r == TypeRun.RUNTIME:
#            pass  # Let's just execute this object
#        elif type_r == TypeRun.VM:
#            # Let's return this object under VMed form
#            # Loop through all children and launch them
#            print('Running', self.type, self.name)
#            for child in self.children:
#                child.run(type_r)
