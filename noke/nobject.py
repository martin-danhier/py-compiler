from enum import Enum
import json
from noke import error
import regex as re

#get the regex and store it (OMFG) globally to avoid recreating it many times.
with open('data/grammar_rules.json', 'r') as json_file:
    rules = json.load(json_file)
full_regex = "|".join("(?P<%s>%s)" % (rule, rules[rule]) for rule in rules)

del(rules) #delete the rules dictionnary that is not needed anymore
del(json_file)



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

class NObjectPosition:
    """ Represents the position of a NObject in the source code. Used for debugging and error localisation."""
    file : str
    start_line : int
    start_column : int
    end_column : int
    end_line : int

    def __init__(self, file : str, start_line : int, start_column : int, end_line : int, end_column : int):
        self.file = file
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column

class NObject:
    """ The base class. Should never be directly instanciated, instantiate one of its children instead."""
    parent : object
    children : list
    #position : object

    def __init__(self, parent = None):
        """ Create a NObject. 
        Parameters
        ----------
        parent : the NObject of which this one is the children. Leave it to None !"""
        self.parent = parent
        self.children = []
        # process body


    def get_stack_trace(self):
        """ Get a stacktrace from this NObject. 
        Returns
        -------
        stack_trace : a str that countains many infos to find this NObject again in the code"""

        stack_trace = '\tin File: "%s" in %s. Details TODO\n' % ('test.idk', self.__class__.__name__)
        if self.parent != None:
            stack_trace += self.parent.get_stack_trace()
        return stack_trace
    
    def scan_declaration(self, match):
        """ Called when a declaration is found in the source code. """
        #get the type
        decl_type = ""
        decl_type_a = match.group("DECL_TYPE_A")
        decl_type_b = match.group("DECL_TYPE_B")
        if (decl_type_a != "var" and decl_type_b != None):
            #error: max 1 type -> 10
            err = error.Error(10,stack=self.get_stack_trace())
            err.launch()    
        elif (decl_type_a == "var" and decl_type_b == None):
            #error: "var" auto selecter not implemented -> 8
            err = error.Error(8,stack=self.get_stack_trace())
            err.launch()                    
        elif (decl_type_a == "var" and decl_type_b != None):
            decl_type = decl_type_b
        elif (decl_type_a != "var" and decl_type_b == None):
            decl_type = decl_type_a
        del(decl_type_a,decl_type_b)
        #save the declaration
        self.children.append(Declaration(decl_type,match.group("DECL_ID"),self))
    

    def scan_module(self, match):
        """ Called when a module is found in the source code. """
        if match.group("MODULE_TYPE") == "module":
            print(match.lastgroup)
        elif match.group("MODULE_TYPE") == "fun":
            #get the return type
            return_type_a = match.group("RETURN_TYPE_A")
            return_type_b = match.group("RETURN_TYPE_B")
            return_type = None
            if ( return_type_a != None and return_type_b != None):
                #two return types given -> 7
                err = error.Error(7,stack=self.get_stack_trace())
                err.launch()
            elif (return_type_a != None):
                return_type = return_type_a
            elif (return_type_b != None):
                return_type = return_type_b
            del(return_type_a,return_type_b)
            #save the function and launch its own analyse
            self.children.append(Fun(match.group("BODY"),match.group("MODULE_ID"),match.group("PARAMETERS"),return_type,self))
        elif match.group("MODULE_TYPE") == "class":
            #not implemented -> 12
            error.Error(12, stack=self.get_stack_trace()).launch()
            #TODO
            pass
        else: 
            #not module in module -> regex_failed
            err = error.Error(msg="Regex failed to match. Expected MODULE, but found %s." % match.lastgroup)
            err.launch()
    
    def scan_fun_body(self, match):
        """Called when parsing a function body"""
        if (match.lastgroup == "MODULE"):
            self.scan_module(match)
        elif (match.lastgroup == "DECLARATION"):                  
            self.scan_declaration(match)
        elif (match.lastgroup == "ASSIGNEMENT"):
            self.children.append(Assignement(match.group("ASSIGN_VAR_ID"),match.group("ASSIGN_VALUE"),match.group("ASSIGN_TYPE"),self))
        elif (match.lastgroup == "CALL"):
            self.children.append(Call(match.group("CALL_ID"),match.group("CALL_ARGUMENTS"), self))
        elif (match.lastgroup == "BRANCH"):
            self.children.append(Branch(match.group("IF_CONDITION"),match.group("IF_BODY"),match.group("ELSE_BODY"),self))
        elif (match.lastgroup == "WHILE_LOOP"):
            self.children.append(While(match.group("WHILE_CONDITION"),match.group("WHILE_BODY"),False,self))
        elif (match.lastgroup == "DO_LOOP"):
            self.children.append(While(match.group("DO_CONDITION"),match.group("DO_BODY"), True, self))
        elif (match.lastgroup == "FOR_LOOP"):
            self.children.append(For(match.group("FOR_ARGUMENTS"),match.group("FOR_BODY"), self))
        elif (match.lastgroup == "RETURN"):
            self.children.append(Return(match.group("RETURN_VALUE"),self))
        #SWITCH TODO
        else:
            #Invalid instruction inside the function body -> 11
            err = error.Error(11, stack=self.get_stack_trace())
            err.launch()

class Module(NObject):
    """ A module is a set of other modules, like fun or Classes.
    => init must check that children are exclusively modules"""
    identifier: str  # the name of the module

    def __init__(self, body: str, identifier: str, parent = None):
        """ Instanciates a module. A module is a set of other modules, like funs or classes.
        Parameters
        ----------
        body: the code inside the module's brackets (not included) (str)
        identifier: the "name" of the module. Should respect naming conventions. (str)
        parent: the NObject of which this one is the children. Leave it to None !"""
        NObject.__init__(self, parent)
        self.identifier = identifier
        #Process body
        for match in re.finditer(full_regex, body):
            if match.lastgroup == "MISMATCH":
                # Regex failed to match -> 1
                # <=> SOMEBODY WROTE SHIT INTO THE CODE FILE ITS NOT MY PROBLEM JERRY
                # But I'm kind : let's try to find the nearest match to give a hint to the user
                if match.group()[0] == ':':
                    #maybe they tried a declaration ?
                    err = error.Error(9, stack=self.get_stack_trace())
                else:
                    err = error.Error(1)
                err.launch()
            # skip those
            elif match.lastgroup not in ["SKIP", "COMMENT", "SEPARATOR", "DISABLE"] and match.group("DISABLED") == None:
                if self.__class__.__name__ == "Module": #in a module, there can only be other modules
                    self.scan_module(match)
                elif self.__class__.__name__ == "Fun": #in a function, there can also be instructions, branches, loops
                    self.scan_fun_body(match)
                elif self.__class__.__name__ == "Class": #class TODO
                    #not implemented -> 12
                    error.Error(12, stack=self.get_stack_trace()).launch()


class Fun(Module):
    """A function is... a function.
    => init must analyse the parameters
    """
    return_type: str
    parameters: list

    def __init__(self, body: str, identifier: str, parameters: str, return_type: str, parent = None):
        Module.__init__(self, body, identifier, parent)
        if return_type != None:
            self.return_type = return_type
        else:
            self.return_type = "void"
        # process parameters

class Class(Module):
    # TODO
    pass


class Condition(NObject):
    """ ex:"if (x > 2) { thing } else {}" is a Conditional instruction
        it has the particulary to have 2 children : if and else (else ifs are just ifs in the else of another if)
        if there is no else statement, else_condition and else_children are None and are skipped when the condition is false
       """
    condition: list  # to revise
    else_condition: list  # to revise too
    else_children: []


class While(NObject):
    # Repeat as long as the condition is true
    def __init__(self, loop_condition, body, do_while : bool, parent = None):
        NObject.__init__(self,parent)
        self.do_while = do_while
        #process condition and body
        

class For(NObject):
    # Ex: for (int i = 0 to 3 step 4)
    def __init__(self, arguments, body, parent = None):
        NObject.__init__(self, parent)
        #process parameters
        


class Declaration(NObject):
    """ex: "int a;" """
    def __init__(self, type, id, parent = None):
        NObject.__init__(self,parent)
        #process data
        for match in re.finditer(full_regex, type):
            if (match.lastgroup not in [COMMENT])
        self.type = type
        self.id = id
        

class Assignement(NObject):
    """ex: "int a = 2" """
    def __init__(self, id, value, type, parent = None):
        NObject.__init__(self, parent)
        self.id = id
        #to be scanned
        self.value = value
        self.type = type
        

class Call(NObject):
    """ex: "print("hello", 2)" """
    def __init__(self, id, arguments, parent = None):
        NObject.__init__(self,parent)
        self.id = id
        #process arguments
        

class Return(NObject):
    """Exit point of a function."""
    def __init__(self, return_value, parent = None):
        NObject.__init__(self, parent)
        #process return value
        

class Branch(NObject):
    """if, else etc"""
    def __init__(self, if_condition, if_body, else_body, parent = None):
        NObject.__init__(self, parent)
        #process condition and bodies
        
    


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
