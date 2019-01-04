import re
import json

class Token:
    nature : str
    value : str

    #constructor
    def __init__(self, nature : str, value : str):
        """ Initialize a Token object.
        Parameters
        ----------
        nature: the nature of the Token (str)
        value: the value of the Token (str)
        """
        self.nature = nature
        self.value = value

    def __repr__(self):
        return ("Token(nature = \"%s\", value = \"%s\")" % (self.nature, self.value))

def tokenize(string : str, grammar_file : str = "grammar_rules.json", log : bool = False ):
    """ Tokenizes the given string using the given grammar file's regex grouping rules.

    Parameters
    ----------
    string : the string to tokenize (str)
    grammar_file : the path to a .json file containing a dict of format { nature (str) : regex (str) }.
    log : if True, the function will print its results in the console (bool)

    Returns
    -------
    token_list : a list of Token objects.
    """
    #Get the grammar rules in the .json file
    with open(grammar_file,'r') as json_file:
        grammar_rules = json.load(json_file)
    #merge them together in a mega grouping regex
    full_regex = "|".join("(?P<%s>%s)" % (rule, grammar_rules[rule]) for rule in grammar_rules)
    token_list = []

    #for each match, check for errors or skips then save the corresponding Token in the list
    for match in re.finditer(full_regex, string):
        if (match.lastgroup == "MISMATCH"): #error
            if log:
                print('%d - Syntax Error' % match.pos)
            break #will be a raise don't kill me please
        elif (match.lastgroup != "SKIP"):
            if log:
                print('%s : %s' % (match.group(), match.lastgroup))
            token_list.append(Token(match.lastgroup,match.group()))
    return token_list

#test
expr = """
int test = 42;
float test2 = .54f;
print ("My name is Jack");
"""
print(tokenize(expr,log=True))


