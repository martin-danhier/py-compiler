import regex as re
import json
from enum import Enum
from noke import error, tools

# initialization
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

    #def __repr__(self):
    #    return 'Object in %s, at %s.' % (self.file, self.start)

    def __init__(self, file: str, start):
        self.file = file
        self.start = start

class NObject:
    """ The base class. Should never be directly instanciated, instantiate one of its children instead."""
    parent: object
    #position : object

    def __init__(self, position = 0, parent=None):
        """ Create a NObject. 
        Parameters
        ----------
        parent : the NObject of which this one is the children. Leave it to None !"""
        self.parent = parent
        if parent != None:
            self.position = NObjectPosition(self.parent.position.file, position)

    def convert_to_dict(self):
        """Converts the NObject to a dictionnary json-able"""
        attr_dict = self.__dict__
        dict = {}
        dict['class_name'] = self.__class__.__name__
        for attr in attr_dict:
            if attr != 'parent':
                
                if isinstance(attr_dict[attr], NObject) or isinstance(attr_dict[attr], Identifier):
                    dict[attr] = attr_dict[attr].convert_to_dict()
                elif attr == 'position':
                    dict['start'] = attr_dict[attr].start
                elif isinstance(attr_dict[attr], list):
                    dict[attr] = [elem.convert_to_dict() for elem in attr_dict[attr]]
                else:
                    dict[attr] = attr_dict[attr]
        return dict
        

    def get_root(self):
        obj = self
        while(True):
            if obj.parent == None:
                return obj
            else:
                obj = obj.parent

    def get_stack_trace(self):
        """ Get a stacktrace from this NObject. 
        Returns
        -------
        stack_trace : a str that countains many infos to find this NObject again in the code"""
        stack_trace = '\tin File "%s", at %s, in %s\n' % (self.position.file, tools.get_coords_from_position(self.position.start, self.position.file), self.__class__.__name__)
        if self.parent != None:
            stack_trace = self.parent.get_stack_trace() + stack_trace
        return stack_trace

    def scan_module(self, match, parent_scan_position = 0):
        """ Called when a module is found in the source code. 

        Parameters
        ----------
        match : a regex match of a module. (Match)
        parent_scan_position : the position of the string scanned in the parent. (int) Ex:
            module test { #body }
            If a module is found in the body, parent_scan_position would be its position
            in the module. """

        if match.group('MODULE_TYPE') == 'module':
            if match.group('RETURN_TYPE_A') != None or match.group('RETURN_TYPE_B') != None:
                if match.group('RETURN_TYPE_A') != None:
                    position = NObjectPosition(self.position.file, parent_scan_position + match.start('RETURN_TYPE_A'))
                elif match.group('RETURN_TYPE_B') != None:
                    position = NObjectPosition(self.position.file, parent_scan_position + match.start('RETURN_TYPE_B'))
                # A module has no return type -> 19
                error.ThrowError(19, position , self.get_stack_trace())
            if match.group('PARAMETERS') != None:
                # A module has no parameters -> 20
                error.ThrowError(20, NObjectPosition(self.position.file, parent_scan_position + match.start('PARAMETERS')), self.get_stack_trace())
            return Module(match, self, parent_scan_position)
        elif match.group('MODULE_TYPE') == 'fun':
            
            # save the function and launch its own analyse
            return Fun(match, self, parent_scan_position)
        elif match.group("MODULE_TYPE") == "class":
            # not implemented -> 14
            error.ThrowError(14, NObjectPosition(self.position.file, parent_scan_position + match.start()), self.get_stack_trace())
            # TODO
            pass
        else:
            # not module in module -> syntax_error
            error.ThrowError(position= NObjectPosition(self.position.file, parent_scan_position + match.start()),msg="Expected MODULE, but found %s." % match.lastgroup, type="syntax_error")

    

    def scan_fun_body(self, match, parent_scan_position):
        """Called when parsing a function body"""
        if match.lastgroup == 'MODULE':
            return self.scan_module(match, parent_scan_position)
        elif match.lastgroup == 'DECLARATION':
            return Declaration(match, self, parent_scan_position)
        elif match.lastgroup == 'ASSIGNEMENT':
            return Assignement(match, self, parent_scan_position)
        elif match.lastgroup == 'CALL':
            return Call(match, self, parent_scan_position)
        elif match.lastgroup == 'BRANCH':
            return Branch(match, self, parent_scan_position)
        elif match.lastgroup == 'WHILE_LOOP':
            return While(match, False, self, parent_scan_position)
        elif match.lastgroup == 'DO_LOOP':
            return While(match, True, self, parent_scan_position)
        elif match.lastgroup == 'FOR_LOOP':
            return For(match, self, parent_scan_position)
        elif match.lastgroup == 'RETURN':
            return Return(match, self, parent_scan_position)
        # SWITCH TODO
        else:
            # Invalid instruction inside the function body -> 11
            error.ThrowError(11, NObjectPosition(self.position.file, parent_scan_position + match.start()), self.get_stack_trace())

    def is_match_valid(self, match, parent_scan_position):
        """ Checks if the given match is valid.

        Parameters
        ----------
        match : a regex match

        Returns
        -------
        match_is_valid : bool
        parent_scan_position : position of the scan in absolute index

        Notes
        -----
        A match is valid if it's not a MISMATCH, a SEPARATOR, a DISABLE, a COMMENT or a SKIP.

        Raises
        ------
        Error(1) if a MISMATCH is encountered.
        """
        if match.lastgroup == 'MISMATCH':
            # error in syntax -> 1
            if len(match.group()) > 0 and match.group()[0] == '\"':
                #unclosed string -> 24
                error.ThrowError(24, NObjectPosition(self.position.file, parent_scan_position + match.start()), self.get_stack_trace())
            error.ThrowError(1, NObjectPosition(self.position.file, parent_scan_position + match.start()), self.get_stack_trace())
            return False
        elif match.lastgroup in ('SKIP', 'SEPARATOR', 'COMMENT', 'DISABLE'):
            return False
        else:
            return True

    def scan_id(self, source, parent_scan_position):
        for match in re.finditer(full_regex, source):
            if self.is_match_valid(match, parent_scan_position) and match.lastgroup in ('IDENTIFIER', 'PATH'):
                if match.lastgroup == 'IDENTIFIER':
                    # ELEMENTARY PARTICLE -> identifier
                    return Identifier(match.group(), match.start() + parent_scan_position, self)
                else:  # path
                    return Path(match, self, parent_scan_position)
            else:  # error, shouldn't be possible to have because of the regex definition.
                # error -> 12
                error.ThrowError(12, NObjectPosition(self.position.file, parent_scan_position + match.start()), self.get_stack_trace())


    def simplify_term(self, term, error_handling=True):
        temp = tools.custom_strip(term, ' ')
        term = temp[0]
        diff = temp[1]
        while len(term) > 1 and term[0] == '(' and term[-1] == ')':
            temp = tools.custom_strip(term[1:-1], ' ')
            term = temp[0]
            diff += 1 + temp[1]
        if len(term) == 0 and error_handling:
            # error -> there is no term -> 13
            error.ThrowError(13, self.position, self.get_stack_trace())
        return (term, diff)

    def scan_expression(self, source : str, parent_scan_position):
        temp = self.simplify_term(source, False)
        
        source = temp[0]
        parent_scan_position += temp[1] #update scan position in order to keep its accuracy
        del(temp)
        
        if len(source) == 0:
            error.ThrowError(17, self.position, self.get_stack_trace())
        value = None
        for match in re.finditer(full_regex, source):
            if self.is_match_valid(match, parent_scan_position):
                if value != None:
                    # error -> more than one element -> 16
                    error.ThrowError(16, NObjectPosition(self.position.file, parent_scan_position + match.start()), self.get_stack_trace())
                elif match.lastgroup == 'LOGIC_GATE':
                    value = Comparison(match, 'LOG', self, parent_scan_position)
                elif match.lastgroup == 'LOGIC_NOT':
                    value = Comparison(match, 'NOT', self, parent_scan_position)
                elif match.lastgroup == 'COMPARISON':
                    value = Comparison(match, 'COMP', self, parent_scan_position)
                elif match.lastgroup == 'ADDITION':
                    value = Operation(match, 'ADD', self, parent_scan_position)
                elif match.lastgroup == 'MULTIPLICATION':
                    value = Operation(match, 'MU', self, parent_scan_position)
                elif match.lastgroup == 'IDENTIFIER':
                    value = Identifier(match.group(), match.start() + parent_scan_position, self)
                elif match.lastgroup == 'STRING_LITERAL':
                    value = Constant('string', match.group().strip('"'), parent_scan_position + match.start(), self)
                elif match.lastgroup == 'CHAR_LITERAL':
                    value = Constant('char', match.group().strip('\''), match.start() + parent_scan_position, self)
                elif match.lastgroup in ('INT_DEC_LITERAL', 'INT_HEX_LITERAL', 'INT_DEC_LITERAL'):
                    value = Constant('int', int(match.group()), match.start() + parent_scan_position, self)
                elif match.lastgroup == 'BOOL_LITERAL':
                    value = match.group()
                    if value in ('true', 'yep'):
                        value = True
                    else:
                        value = False
                    value = Constant('bool', value, match.start() + parent_scan_position, self)
                elif match.lastgroup == 'FLOAT_LITERAL':
                    value = Constant('float', float(
                        match.group().strip('f')), match.start() + parent_scan_position, self)
                elif match.lastgroup == 'CALL':
                    value = Call(match, self, parent_scan_position)
                elif match.lastgroup == 'PATH':
                    value = Path(match, self, parent_scan_position)
                elif match.lastgroup == 'DOUBLE_LITERAL':
                    value = Constant('double', float(match.group()), match.start() + parent_scan_position, self)
                #ERRORS
                elif len(match.group()) > 0 and match.group()[0] == '\"':
                    #unclosed string -> 24
                    error.ThrowError(24, NObjectPosition(self.position.file, parent_scan_position + match.start()), self.get_stack_trace())
                else:
                    error.ThrowError(1, NObjectPosition(self.position.file, parent_scan_position + match.start()), self.get_stack_trace())
        if value == None:
            # if this is executed, then it didn't found any match. The expression is then invalid.
            error.ThrowError(1, self.position, self.get_stack_trace())
        return value


class Module(NObject):
    """ A module is a set of other modules, like fun or Classes.
    => init must check that children are exclusively modules"""

    ########## NOTE ##########
    # Because of python joy, we cannot split the constructor into two different implementations.
    # In a normal language, you are supposed to split the constructor. Read the comments for details.

    def get_stack_trace(self):
        """ Get a stacktrace from this NObject. 
        Returns
        -------
        stack_trace : a str that countains many infos to find this NObject again in the code"""
        stack_trace = '\tin File "%s", at %s, in %s : "%s"\n' % (self.position.file, tools.get_coords_from_position(self.position.start, self.position.file), self.__class__.__name__, self.identifier)
        if self.parent != None:
            stack_trace = self.parent.get_stack_trace() + stack_trace
        return stack_trace    

    def __init__(self, args, parent=None, parent_scan_position = 0):
        """ Instanciates and recursively parse a module.

            Parameters
            ----------
            args: two possibilities
                A) A tuple that contains (body (str), identifier (str)) => ROOT FILE
                B) A regex Match (Match) => INTERNAL
            parent: The NObject  of which this one is a child. => INTERNAL
            scan_pos_in_parent: position of the scan in the parent (ex: pos of the body in the module). (int) => INTERNAL

            Notes
            -----
            To instanciate a file, use the format : Module((source_str, file_nam_)).
        """
        if isinstance(args, tuple):
            ########## NOTE ##########
            # constructor 1 : ROOT CONSTRUCTOR
            # Note to the translator:
            # <=> Module(string body, string identifier)
            # As there is no "parent" parameter, no need to check if it's null.
            NObject.__init__(self, parent=parent)
            if parent == None: #root object, like a file
                if len(args[1]) < 5:
                    #File name is too short or invalid -> 5
                    error.ThrowError(5)
                elif args[1][-4:] != '.idk':
                    #File is not of the correct file format -> 5
                    error.ThrowError(5)
                self.position = NObjectPosition(args[1], 0)
                self.identifier = Identifier(args[1][:-4], 0, self)
                # Process body
                self.children = []
                for match in re.finditer(full_regex, args[0]):
                    if match.lastgroup == 'MISMATCH':
                        # Regex failed to match -> 1
                        # <=> SOMEBODY WROTE SHIT INTO THE CODE FILE ITS NOT MY PROBLEM JERRY
                        error.ThrowError(1, NObjectPosition(self.position.file, match.start()), self.get_stack_trace())
                    # skip those
                    elif match.lastgroup not in ('SKIP', 'COMMENT', 'SEPARATOR', 'DISABLE') and match.group('DISABLED') == None:
                        if self.__class__.__name__ == 'Module':  # in a module, there can only be other modules
                            self.children.append(self.scan_module(match, 0))
                        elif self.__class__.__name__ == 'Fun':  # in a function, there can also be instructions, branches, loops
                            self.children.append(self.scan_fun_body(match, 0))
                        elif self.__class__.__name__ == 'Class':  # class TODO
                            # not implemented -> 14
                            # not going to raise for now because it is raised before (scan_module)
                            error.ThrowError(14, self.position, self.get_stack_trace())

                
            else:
                #root file constructor used internally -> NoKe Programming Error
                # -> 22
                error.ThrowError(22, self.position, self.get_stack_trace())
            
        else:
            ########## NOTE ##########
            # constructor 2 : INTERNAL CONSTRUCTOR
            # Note to the translator:
            # <=> Module(Match match, NObject parent, int scan_pos_in_parent = 0)
            # Maybe rename all the "match" below in "submatch" and all the "args" below in "match"
            # => Can be a protected constructor, as it is only used internally.
            # As it is an internal constructor, parent MUST be a NObject and non-null.
            if parent == None:
                # internal constructor used externally -> 23
                error.ThrowError(23)
            else:
                NObject.__init__(self, args.start() + parent_scan_position, parent)
                self.identifier = Identifier(args.group('MODULE_ID'), args.start('MODULE_ID') + parent_scan_position, self)
                self.children = []
                # Process body
                for match in re.finditer(full_regex, args.group('BODY')):
                    if self.is_match_valid(match, parent_scan_position + args.start('BODY')):
                        if self.__class__.__name__ == 'Module':  # in a module, there can only be other modules
                            self.children.append(self.scan_module(match, parent_scan_position + args.start('BODY')))
                        elif self.__class__.__name__ == 'Fun':  # in a function, there can also be instructions, branches, loops
                            self.children.append(self.scan_fun_body(match, parent_scan_position + args.start('BODY')))
                        elif self.__class__.__name__ == 'Class':  # class TODO
                            # not implemented -> 14
                            # no gonna raise etc
                            error.ThrowError(14, self.position, self.get_stack_trace())


class Fun(Module):
    """A function is... a function.
    => init must analyse the parameters
    """
    return_type: str
    parameters: list

    def __init__(self, match, parent, parent_scan_position):
        """ INTERNAL CONSTRUCTOR """
        Module.__init__(self, match, parent, parent_scan_position)

        # get the return type
        return_type = None

        return_type_a = match.group('RETURN_TYPE_A')
        return_type_b = match.group('RETURN_TYPE_B')
        if (return_type_a != None and return_type_b != None):
            # two return types given -> 7
            error.ThrowError(7, NObjectPosition(self.position.file, parent_scan_position + match.start('RETURN_TYPE_A')),self.get_stack_trace())
        elif (return_type_a != None):
            self.return_type = self.scan_id(return_type_a, match.start('RETURN_TYPE_A'))
        elif (return_type_b != None):
            self.return_type = self.scan_id(return_type_b, match.start('RETURN_TYPE_B'))
        else:
            self.return_type = Identifier('void', parent_scan_position, self) #that or identifier with "void" inside
        # process parameters
        # maybe remake some of this to check if every rule is followed
        self.parameters = []
        temp = self.simplify_term(match.group('PARAMETERS'), False)
        for m in re.finditer(full_regex, temp[0]):
            if self.is_match_valid(m, parent_scan_position + m.start() + temp[1] + match.start('PARAMETERS')) and m.lastgroup != 'PARAM_SEPARATOR':
                if m.lastgroup in ('DECLARATION', 'ASSIGNEMENT'):
                    self.parameters.append(self.scan_fun_body(m, parent_scan_position + temp[1] + m.start() + match.start('PARAMETERS')))
                else:
                    #something else -> 25
                    
                    error.ThrowError(25, NObjectPosition(self.position.file, parent_scan_position + temp[1] + m.start() + match.start('PARAMETERS')), self.get_stack_trace())





class Class(Module):
    # TODO
    pass


class While(NObject):
    # Repeat as long as the condition is true
    def __init__(self, match, do_while: bool, parent, parent_scan_position):
        NObject.__init__(self, match.start() + parent_scan_position, parent)
        self.do_while = do_while
        prefix = ''
        if do_while:
            prefix = 'DO'
        else:
            prefix = 'WHILE'
        self.loop_condition = self.scan_expression(match.group(prefix + '_CONDITION'), parent_scan_position + match.start(prefix + '_CONDITION'))
        self.children = []
        for m in re.finditer(full_regex, match.group(prefix + '_BODY')):
            if self.is_match_valid(m, parent_scan_position + match.start(prefix + '_BODY')):
                self.children.append(self.scan_fun_body(m, parent_scan_position + match.start(prefix + '_BODY')))

class For(NObject):
    # Ex: for (int i = 0 to 3 step 4)
    def __init__(self, match, parent, parent_scan_position):
        NObject.__init__(self, match.start() + parent_scan_position, parent)
        #process body
        self.children = []
        for m in re.finditer(full_regex, match.group('FOR_BODY')):
            if self.is_match_valid(m, parent_scan_position + match.start('FOR_BODY')):
                self.children.append(self.scan_fun_body(m,parent_scan_position + match.start('FOR_BODY')))
        #process start
        for m in re.finditer (full_regex, match.group('FOR_START')):
            if self.is_match_valid(m, parent_scan_position + match.start('FOR_START')):
                if m.lastgroup == 'ASSIGNEMENT':
                    self.start = Assignement(m, self, parent_scan_position + match.start('FOR_START'))
                else:
                    # not an assignement -> 21
                    error.ThrowError(21, NObjectPosition(self.position.file, parent_scan_position + match.start('FOR_START')), self.get_stack_trace())
        #process end 
        if match.group('FOR_END_KW') == 'to':
            #to => [start] < [end]
            temp = self.simplify_term(match.group('FOR_END'), False)
            
            for m in re.finditer(full_regex, '%s<(%s)' % (self.start.id, temp[0])):
                if self.is_match_valid(m, parent_scan_position + temp[1] + match.start('FOR_END')):
                    self.condition = Comparison(m, 'COMP', self, parent_scan_position + temp[1] + match.start('FOR_END'), True)
        else:
            self.condition = self.scan_expression(match.group('FOR_END'), parent_scan_position + match.start('FOR_END'))
        #process step
        step = match.group('FOR_STEP')
        if (step == None):
            self.step = Constant('int', 1, parent_scan_position + match.start(), self )
        else:
            self.step = self.scan_expression(step, parent_scan_position + match.start('FOR_STEP'))
        


class Declaration(NObject):
    """ex: "int a;" """

    def __init__(self, match, parent, parent_scan_position):
        NObject.__init__(self, match.start() + parent_scan_position, parent)
        
        # get the type
        decl_type_a = match.group("DECL_TYPE_A")
        decl_type_b = match.group("DECL_TYPE_B")
        if (decl_type_a not in ['var', None] and decl_type_b != None):
            # error: max 1 type -> 10
            error.ThrowError(10, self.position, self.get_stack_trace())

        elif (decl_type_a == "var" and decl_type_b == None):
            # error: "var" auto selecter not implemented -> 8
            error.ThrowError(8, self.position, self.get_stack_trace())

        elif (decl_type_a == None and decl_type_b != None):
            #Expected var keyword -> 9
            error.ThrowError(9, NObjectPosition(self.position.file, parent_scan_position + match.start('DECL_ID')), self.get_stack_trace())

        elif (decl_type_a == "var" and decl_type_b != None):
            self.type = self.scan_id(decl_type_b, match.start('DECL_TYPE_B') + parent_scan_position)
        elif (decl_type_a != "var" and decl_type_b == None):
            self.type = self.scan_id(decl_type_a, match.start('DECL_TYPE_A') + parent_scan_position)
        del(decl_type_a, decl_type_b)

        # scan id, it can only be an identifier (regex)
        self.id = Identifier(match.group('DECL_ID'), match.start('DECL_ID') + parent_scan_position,self)


class Assignement(NObject):
    """ex: "int a = 2" """
    def __repr__(self):
        if type == None:
            return '%s = %s' % (self.id, self.value)
        else:
            return '%s %s = %s' % (self.type, self.id, self.value)


    def __init__(self, match, parent=None, parent_scan_position = 0):
        NObject.__init__(self, match.start() + parent_scan_position, parent)
        self.id = self.scan_id(match.group('ASSIGN_VAR_ID'), parent_scan_position + match.start('ASSIGN_VAR_ID'))
        # type included <=> Declaration
        if match.group('ASSIGN_TYPE') != None:
            self.type = self.scan_id(match.group('ASSIGN_TYPE'), parent_scan_position + match.start('ASSIGN_TYPE'))
        else:
            self.type = None
        # scan value
        self.value = self.scan_expression(match.group('ASSIGN_VALUE'), match.start('ASSIGN_VALUE') + parent_scan_position)


class Call(NObject):
    """ex: "print("hello", 2)" """

    def __init__(self, match, parent = None, parent_scan_position = 0):
        NObject.__init__(self, match.start() + parent_scan_position, parent)
        self.id = self.scan_id(match.group('CALL_ID'), parent_scan_position + match.start('CALL_ID'))

        self.arguments = []
        arguments = match.group('CALL_ARGUMENTS')
        if arguments != None:
            if ';' in arguments:
                error.ThrowError(15, self.position, self.get_stack_trace())
            # process arguments
            for m in re.finditer(full_regex, arguments):
                if self.is_match_valid(m, parent_scan_position + m.start() + match.start('CALL_ARGUMENTS')) and m.lastgroup != 'PARAM_SEPARATOR':
                    self.arguments.append(self.scan_expression(m.group(), parent_scan_position + m.start() + match.start('CALL_ARGUMENTS')))


class Return(NObject):
    """Exit point of a function."""

    def __init__(self, match, parent, parent_scan_position):
        NObject.__init__(self , match.start() + parent_scan_position, parent)
        self.return_value = self.scan_expression(match.group('RETURN_VALUE'), parent_scan_position + match.start('RETURN_VALUE'))


class Branch(NObject):
    """if, else etc"""

    def __init__(self, match, parent, parent_scan_position):
        NObject.__init__(self, match.start() + parent_scan_position, parent)
        # process condition. A non-boolean value will be true if different from null.
        self.if_condition = self.scan_expression(match.group('IF_CONDITION'), parent_scan_position + match.start('IF_CONDITION'))
        # process if_body
        self.if_body = []
        for m in re.finditer(full_regex, match.group('IF_BODY')):
            if self.is_match_valid(m, parent_scan_position):
                self.if_body.append(self.scan_fun_body(m, parent_scan_position + match.start('IF_BODY') ))
        # process else_body
        self.else_body = []
        if match.group('ELSE_BODY') != None:
            for m in re.finditer(full_regex, match.group('ELSE_BODY')):
                if self.is_match_valid(m, parent_scan_position + match.start('ELSE_BODY')):
                    self.else_body.append(self.scan_fun_body(m, parent_scan_position + match.start('ELSE_BODY')))


class Path(NObject):
    """Ex: "Person.Name" """
    def __repr__(self):
        return '%s.%s' % (self.left_term, self.right_term)

    def __init__(self, match, parent, parent_scan_position):
        NObject.__init__(self, match.start() + parent_scan_position, parent)
        # Process right term
        self.right_term = Identifier(match.group('PATH_RIGHT_ID'), match.start('PATH_RIGHT_ID') + parent_scan_position ,self)
        # Process left term
        self.left_term = self.scan_id(match.group('PATH_LEFT_ID'), match.start('PATH_LEFT_ID') + parent_scan_position)


class Comparison(NObject):
    def __repr__(self):
        if self.parent.__class__.__name__ in ['Comparison', 'Operation']:
            return '(%s %s %s)' % (self.left_term, self.operator, self.right_term)
        else:
            return '%s %s %s' % (self.left_term, self.operator, self.right_term)

    def __init__(self, match, prefix, parent=None, parent_scan_position = 0, invisible_left_term = False):
        NObject.__init__(self, match.start() + parent_scan_position, parent)
        if invisible_left_term:
            #used in For loop when an implicit condition is considered.
            #The only apparent element is the right term, so it should count from there.
            parent_scan_position -= match.start(prefix + '_RIGHT_TERM') + 1 #-1 because a one appeared somewhere, maybe because it is 0-based ?
        temp = self.simplify_term(match.group(prefix + '_LEFT_TERM'))
        self.left_term = self.scan_expression(temp[0], parent_scan_position + temp[1] + match.start(prefix + '_LEFT_TERM'))
        if match.group(prefix + '_RIGHT_TERM') != None:
            temp = self.simplify_term(match.group(prefix + '_RIGHT_TERM'))
            self.right_term = self.scan_expression(
                temp[0], parent_scan_position + temp[1] + match.start(prefix + '_RIGHT_TERM'))
        elif match.group(prefix + '_OPERATOR') != 'not':
            # empty term -> 13
            error.ThrowError(13, self.position, self.get_stack_trace())
        
        self.operator = match.group(prefix + '_OPERATOR')


class Operation(Comparison):
    def __init__(self, match, prefix,  parent=None, parent_scan_position = 0):
        # Math operations behave exactly like a logical operation, but
        # I made two classes in order to be able to know which one it is
        Comparison.__init__(self, match, prefix, parent, parent_scan_position)


###### ELEMENTARY PARTICLES ######
# These are indivisible NObjects, and stop the recursion.

class Constant(NObject):
    def __repr__(self):
        if self.type == 'bool':
            if self.value == True:
                return 'true'
            else:
                return 'false'
        else:
            return str(self.value)

    def __init__(self, type, value, position = 0, parent=None):
        NObject.__init__(self, position, parent)
        self.type = type
        self.value = value


class Identifier(NObject):
    def __repr__(self):
       return self.id

    def __init__(self, id, position = 0, parent = None):
        NObject.__init__(self, position, parent)
        self.id = id
