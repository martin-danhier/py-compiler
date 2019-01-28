import regex as re
from enum import Enum
import json
from noke import error


# get the regex and store it (OMFG) globally to avoid recreating it many times.
with open('data/grammar_rules.json', 'r') as json_file:
    rules = json.load(json_file)
full_regex = "|".join("(?P<%s>%s)" % (rule, rules[rule]) for rule in rules)
del(rules)  # delete the rules dictionnary that is not needed anymore
del(json_file)
class NObjectRun(Enum):
    # Type of run
    ASS = 1  # Compile to binary
    VM = 2  # Compile it to VMed


class NObjectPosition:
    """ Represents the position of a NObject in the source code. Used for debugging and error localisation."""
    file: str
    start_line: int
    start_column: int
    end_column: int
    end_line: int

    def __init__(self, file: str, start_line: int, start_column: int, end_line: int, end_column: int):
        self.file = file
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column


class NObject:
    """ The base class. Should never be directly instanciated, instantiate one of its children instead."""
    parent: object
    children: list
    #position : object

    def __init__(self, parent=None):
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

        stack_trace = '\tin File: "%s" in %s. Details TODO\n' % (
            'test.idk', self.__class__.__name__)
        if self.parent != None:
            stack_trace += self.parent.get_stack_trace()
        return stack_trace

    def scan_declaration(self, match):
        """ Called when a declaration is found in the source code. """
        # get the type
        decl_type = ""
        decl_type_a = match.group("DECL_TYPE_A")
        decl_type_b = match.group("DECL_TYPE_B")
        if (decl_type_a != "var" and decl_type_b != None):
            # error: max 1 type -> 10
            err = error.Error(10, stack=self.get_stack_trace())
            err.launch()
        elif (decl_type_a == "var" and decl_type_b == None):
            # error: "var" auto selecter not implemented -> 8
            err = error.Error(8, stack=self.get_stack_trace())
            err.launch()
        elif (decl_type_a == "var" and decl_type_b != None):
            decl_type = decl_type_b
        elif (decl_type_a != "var" and decl_type_b == None):
            decl_type = decl_type_a
        del(decl_type_a, decl_type_b)
        # save the declaration
        self.children.append(Declaration(
            decl_type, match.group("DECL_ID"), self))

    def scan_module(self, match):
        """ Called when a module is found in the source code. """
        return_type_a = match.group("RETURN_TYPE_A")
        return_type_b = match.group("RETURN_TYPE_B")

        if match.group("MODULE_TYPE") == "module":
            if (return_type_a != None or return_type_b != None):
                #A module has no return type -> 19
                error.Error(19, stack=self.get_stack_trace()).launch()
            if match.group("PARAMETERS") != None:
                #A module has no parameters -> 20
                error.Error(20, stack=self.get_stack_trace()).launch()
            self.children.append(Module(match.group('BODY'),match.group('MODULE_ID'),self))
        elif match.group("MODULE_TYPE") == "fun":
            # get the return type
            return_type = None
            if (return_type_a != None and return_type_b != None):
                # two return types given -> 7
                err = error.Error(7, stack=self.get_stack_trace())
                err.launch()
            elif (return_type_a != None):
                return_type = return_type_a
            elif (return_type_b != None):
                return_type = return_type_b
            del(return_type_a, return_type_b)
            # save the function and launch its own analyse
            self.children.append(Fun(match.group("BODY"), match.group(
                "MODULE_ID"), self.simplify_term(match.group("PARAMETERS"), False), return_type, self))
        elif match.group("MODULE_TYPE") == "class":
            # not implemented -> 12
            error.Error(12, stack=self.get_stack_trace()).launch()
            # TODO
            pass
        else:
            # not module in module -> regex_failed
            err = error.Error(
                msg="Regex failed to match. Expected MODULE, but found %s." % match.lastgroup)
            err.launch()

    def scan_fun_body(self, match):
        """Called when parsing a function body"""
        if (match.lastgroup == "MODULE"):
            self.scan_module(match)
        elif (match.lastgroup == "DECLARATION"):
            self.scan_declaration(match)
        elif (match.lastgroup == "ASSIGNEMENT"):
            self.children.append(Assignement(match.group("ASSIGN_VAR_ID"), match.group(
                "ASSIGN_VALUE"), match.group("ASSIGN_TYPE"), self))
        elif (match.lastgroup == "CALL"):
            self.children.append(
                Call(match.group("CALL_ID"), match.group("CALL_ARGUMENTS"), self))
        elif (match.lastgroup == "BRANCH"):
            self.children.append(Branch(match.group("IF_CONDITION"), match.group(
                "IF_BODY"), match.group("ELSE_BODY"), self))
        elif (match.lastgroup == "WHILE_LOOP"):
            self.children.append(
                While(match.group("WHILE_CONDITION"), match.group("WHILE_BODY"), False, self))
        elif (match.lastgroup == "DO_LOOP"):
            self.children.append(
                While(match.group("DO_CONDITION"), match.group("DO_BODY"), True, self))
        elif (match.lastgroup == "FOR_LOOP"):
            self.children.append(
                For(match.group("FOR_ARGUMENTS"), match.group("FOR_BODY"), self))
        elif (match.lastgroup == "RETURN"):
            self.children.append(Return(match.group("RETURN_VALUE"), self))
        # SWITCH TODO
        else:
            # Invalid instruction inside the function body -> 11
            err = error.Error(11, stack=self.get_stack_trace())
            err.launch()

    def is_match_valid(self, match):
        """ Checks if the given match is valid.

        Parameters
        ----------
        match : a regex match

        Returns
        -------
        match_is_valid : bool

        Notes
        -----
        A match is valid if it's not a MISMATCH, a SEPARATOR, a DISABLE, a COMMENT or a SKIP.

        Raises
        ------
        Error(1) if a MISMATCH is encountered.
        """
        if match.lastgroup == 'MISMATCH':
            # error in syntax -> 1
            error.Error(1, stack=self.get_stack_trace()).launch()
            return False
        elif match.lastgroup in ('SKIP', 'SEPARATOR', 'COMMENT', 'DISABLE'):
            return False
        else:
            return True

    def scan_id(self, source):
        for match in re.finditer(full_regex, source):
            if self.is_match_valid(match) and match.lastgroup in ('IDENTIFIER', 'PATH'):
                if match.lastgroup == 'IDENTIFIER':
                    # ELEMENTARY PARTICLE -> identifier
                    return Identifier(match.group(), self)
                else:  # path
                    return Path(match.group('PATH_LEFT_ID'), match.group('PATH_RIGHT_ID'), self)
            else:  # error, shouldn't be possible to have because of the regex definition.
                # error -> 12
                error.Error(12, stack=self.get_stack_trace()).launch()

    def simplify_term(self, term, error_handling=True):
        term = term.strip(' ')
        while len(term) > 1 and term[0] == '(' and term[-1] == ')':
            term = term[1:-1].strip(' ')
        if len(term) == 0 and error_handling:
            # error -> there is no
            #  term -> 13
            error.Error(13, stack=self.get_stack_trace()).launch()
        return term

    def scan_expression(self, source):
        source = self.simplify_term(source, False)
        if len(source) == 0:
            error.Error(17, stack=self.get_stack_trace()).launch()
        value = None
        for match in re.finditer(full_regex, source):
            if self.is_match_valid(match):
                if value != None:
                    # error -> more than one element -> 16
                    error.Error(16, stack=self.get_stack_trace()).launch()
                elif match.lastgroup == 'LOGIC_GATE':
                    value = Comparison(match.group('LOG_LEFT_TERM'), match.group(
                        'COMP_OPERATOR'), match.group('LOG_RIGHT_TERM'), self)
                elif match.lastgroup == 'LOGIC_NOT':
                    value = Comparison(match.group(
                        'NOT_TERM'), 'not', None, self)
                elif match.lastgroup == 'COMPARISON':
                    value = Comparison(match.group('COMP_LEFT_TERM'), match.group(
                        'COMPARATOR'), match.group('COMP_RIGHT_TERM'), self)
                elif match.lastgroup == 'ADDITION':
                    value = Operation(match.group('ADD_LEFT_TERM'), match.group(
                        'ADD_OPERATOR'), match.group('ADD_RIGHT_TERM'), self)
                elif match.lastgroup == 'MULTIPLICATION':
                    value = Operation(match.group('MU_LEFT_TERM'), match.group(
                        'MU_OPERATOR'), match.group('MU_RIGHT_TERM'), self)
                elif match.lastgroup == 'IDENTIFIER':
                    value = Identifier(match.group(), self)
                elif match.lastgroup == 'STRING_LITERAL':
                    value = Constant('string', match.group().strip('"'), self)
                elif match.lastgroup == 'CHAR_LITERAL':
                    value = Constant('char', match.group().strip('\''), self)
                elif match.lastgroup in ('INT_DEC_LITERAL', 'INT_HEX_LITERAL', 'INT_DEC_LITERAL'):
                    value = Constant('int', int(match.group()), self)
                elif match.lastgroup == 'BOOL_LITERAL':
                    value = match.group()
                    if value in ('true', 'yep'):
                        value = True
                    else:
                        value = False
                    value = Constant('bool', value, self)
                elif match.lastgroup == 'FLOAT_LITERAL':
                    value = Constant('float', float(
                        match.group().strip('f')), self)
                elif match.lastgroup == 'CALL':
                    value = Call(match.group('CALL_ID'),
                                 match.group('CALL_ARGUMENTS'), self)
                elif match.lastgroup == 'PATH':
                    value = Path(match.group('PATH_LEFT_ID'),
                                 match.group('PATH_RIGHT_ID'), self)
                elif match.lastgroup == 'DOUBLE_LITERAL':
                    value = Constant('double', float(match.group()), self)
                else:
                    error.Error(1, stack=self.get_stack_trace()).launch()
        if value == None:
            # if this is executed, then it didn't found any match. The expression is then invalid.
            error.Error(1, stack=self.get_stack_trace()).launch()
        return value


class Module(NObject):
    """ A module is a set of other modules, like fun or Classes.
    => init must check that children are exclusively modules"""
    identifier: str  # the name of the module

    def __init__(self, body: str, identifier: str, parent=None):
        """ Instanciates a module. A module is a set of other modules, like funs or classes.
        Parameters
        ----------
        body: the code inside the module's brackets (not included) (str)
        identifier: the "name" of the module. Should respect naming conventions. (str)
        parent: the NObject of which this one is the children. Leave it to None !"""
        NObject.__init__(self, parent)
        self.identifier = identifier
        # Process body
        for match in re.finditer(full_regex, body):
            if match.lastgroup == "MISMATCH":
                # Regex failed to match -> 1
                # <=> SOMEBODY WROTE SHIT INTO THE CODE FILE ITS NOT MY PROBLEM JERRY
                # But I'm kind : let's try to find the nearest match to give a hint to the user
                if match.group()[0] == ':':
                    # maybe they tried a declaration ?
                    err = error.Error(9, stack=self.get_stack_trace())
                else:
                    err = error.Error(1, stack=self.get_stack_trace())
                err.launch()
            # skip those
            elif match.lastgroup not in ("SKIP", "COMMENT", "SEPARATOR", "DISABLE") and match.group("DISABLED") == None:
                if self.__class__.__name__ == "Module":  # in a module, there can only be other modules
                    self.scan_module(match)
                elif self.__class__.__name__ == "Fun":  # in a function, there can also be instructions, branches, loops
                    self.scan_fun_body(match)
                elif self.__class__.__name__ == "Class":  # class TODO
                    # not implemented -> 12
                    error.Error(12, stack=self.get_stack_trace()).launch()

        print(self.children)


class Fun(Module):
    """A function is... a function.
    => init must analyse the parameters
    """
    return_type: str
    parameters: list

    def __init__(self, body: str, identifier: str, parameters: str, return_type: str, parent=None):
        Module.__init__(self, body, identifier, parent)
        if return_type != None:
            self.return_type = return_type
        else:
            self.return_type = "void"
        # process parameters


class Class(Module):
    # TODO
    pass


class While(NObject):
    # Repeat as long as the condition is true
    def __init__(self, loop_condition, body, do_while: bool, parent=None):
        NObject.__init__(self, parent)
        self.do_while = do_while
        # process condition and body


class For(NObject):
    # Ex: for (int i = 0 to 3 step 4)
    def __init__(self, arguments, body, parent=None):
        NObject.__init__(self, parent)
        # process parameters


class Declaration(NObject):
    """ex: "int a;" """

    def __init__(self, type, id, parent=None):
        NObject.__init__(self, parent)
        # scan type
        self.type = self.scan_id(type)
        # scan id, it can only be an identifier (regex)
        self.id = id


class Assignement(NObject):
    """ex: "int a = 2" """

    def __init__(self, id, value, type, parent=None):
        NObject.__init__(self, parent)
        self.id = self.scan_id(id)
        # type included <=> Declaration
        if type != None:
            self.type = self.scan_id(type)
        else:
            self.type = None
        # scan value
        self.value = self.scan_expression(value)


class Call(NObject):
    """ex: "print("hello", 2)" """

    def __init__(self, id, arguments, parent=None):
        NObject.__init__(self, parent)
        self.id = self.scan_id(id)

        self.arguments = []
        if arguments != None:
            if ';' in arguments:
                error.Error(15, stack=self.get_stack_trace()).launch()
            # process arguments
            for match in re.finditer(full_regex, arguments):
                if self.is_match_valid(match) and match.lastgroup != 'PARAM_SEPARATOR':
                    self.arguments.append(self.scan_expression(match.group()))


class Return(NObject):
    """Exit point of a function."""

    def __init__(self, return_value, parent=None):
        NObject.__init__(self, parent)
        self.return_value = self.scan_expression(return_value)



class Branch(NObject):
    """if, else etc"""

    def __init__(self, if_condition, if_body, else_body, parent=None):
        NObject.__init__(self, parent)
        # process condition and bodies


class Path(NObject):
    """Ex: "Person.Name" """

    def __init__(self, left_term, right_term, parent=None):
        NObject.__init__(self, parent)
        # Process right term
        self.right_term = Identifier(right_term, self)
        # Process left term
        self.left_term = self.scan_id(left_term)


class Comparison(NObject):
    def __init__(self, left_term, operator, right_term, parent=None):
        NObject.__init__(self, parent)
        self.left_term = self.scan_expression(self.simplify_term(left_term))
        if right_term != None:
            self.right_term = self.scan_expression(
                self.simplify_term(right_term))
        elif operator != 'not':
            # empty term -> 13
            error.Error(13, stack=self.get_stack_trace()).launch()
        self.operator = operator


class Operation(Comparison):
    def __init__(self, left_term, operator, right_term, parent=None):
        # Math operation behaves exactly like a logical operation, but
        # I made two classes in order to be able to know which one it is
        Comparison.__init__(self, left_term, operator, right_term, parent)


###### ELEMENTARY PARTICLES ######
# These are indivisible NObjects, and stop the recursion.

class Constant(NObject):
    def __init__(self, type, value, parent=None):
        NObject.__init__(self, parent)
        self.type = type
        self.value = value


class Identifier(NObject):
    def __init__(self, id, parent):
        NObject.__init__(self, parent)
        self.id = id
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
