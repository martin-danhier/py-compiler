from noke import error

def get_string_info(string):
    """ Calculate the number of lines in a string.
    
    Parameters
    ----------
    string: the input string (str)
    
    Returns
    -------
    length: coords of the last character of the string (Coords) """
    line_count = 1
    column_count = 1
    for char in string:
        if char == '\n':
            column_count = 1
            line_count += 1
        else:
            column_count += 1
    return Coords(line_count, column_count, len(string))


def get_coords_from_position(position, file):
    """ Converts a char-count position to a line-column pair of coords.

    Parameters
    ----------
    position: the char-count position that needs to be converted (int)
    file: path to the file (str)
    
    Returns
    -------
    coords:  object of type (Coords) countaining... the coords.
    
    Notes
    -----
    position needs to be strictly smaller that the length of the file.
    """
    line_counter = 1
    column_counter = 1
    try:
        with open(file, 'r') as source:
            string = source.read()
    except:
        #unable to open file -> 3
        error.ThrowError(3)
    i = 0
    j = position
    while j > 0:
        if string[i] == '\n':
            line_counter += 1
            column_counter = 1
        else:
            column_counter += 1
        i += 1
        j -= 1
    return Coords(line_counter, column_counter, position)

def custom_strip(string, char):
    """Strip a string, but count the number of characters removed at the beginning.
    Parameters
    ----------
    string: the (str) to strip
    char: the char that needs to be removed (str, 1 character)
    
    Returns
    -------
    result: a tuple ( stripped_string (str), diff (int) )"""
    #beginning
    difference = 0
    while len(string) > 0 and string[0] == char:
        string = string[1:]
        difference += 1 #count the number of character removed at the beginning
    #end
    while len(string) > 0 and string[-1] == char:
        string = string[:-1]
    return (string, difference)

class Coords:
    def __init__(self, line : int, column : int, char_counter):
        self.line = line
        self.column = column
        self.char_counter = char_counter
    
    def __repr__(self):
        return '(Ln %s, Col %s)' % (self.line, self.column)