import json, click, os, sys
from noke import error, nobject 
from termcolor import colored
from colorama import init


@click.command()
@click.argument('source_file')
@click.option('--output', '-o', type=str, help='Output file. (Default <source_file>.json)')
@click.option('--interpret/--compile', '-i/-c', help='Convert to json to use with Endiver / Compile to executable. (Default interpret)')
@click.option('--verbose/--silent', '-v/-s' , help='Enable/Disable logs. (Default off)')
@click.option('--override/--ask', '-o/-a', help='Enable/Disable the "always override" mode. (Default off)')
def main(source_file, interpret, output, verbose, override):
    init() #allow coloring on windows
    if os.path.isfile(source_file):
        if len(source_file) > 4 and source_file[-4:] == '.idk':
            try:
                # Open and read the file
                with open(source_file, 'r') as src :
                    source = src.read()
            except:
                # Unable to open file -> 3
                error.ThrowError(3)

            ### PARSER ###
            if verbose:
                print('Parsing %s...' % source_file)
            main_module = nobject.Module((source, source_file))
            
            ### PRE INTERPRETER ###
            if interpret:
                # Check if the output file is valid.
                if output == None:
                    output = source_file[:-4] + '.json'
                elif len(output) < 6 or output[-5:] != '.json':
                    print('NoKe compiler %s: \"%s\" is not a .json file.\n\tA) Continue with this file.\n\tB) Continue with \"%s.json\" instead.\n\tC) Cancel.' % (colored('warning','yellow'), output, source_file[:-4]))
                    answered = False
                    while not answered:
                        answer = input('Enter letter >>> ').strip(' ').lower()
                        if answer == 'a':
                            answered = True
                        elif answer == 'b':
                            answered = True
                            output = source_file[:-4] + '.json'
                        elif answer == 'c':
                            answered = True
                            print('\nAborted!')
                            sys.exit(1)
                        else:
                            print('Invalid answer.\n')
                    print('Continuing with %s.' % output)   
                if os.path.isfile(output) and not override:
                    # file already exists
                    print('NoKe compiler %s: \"%s\" already exists. Overwrite ? (y/n)' % (colored('warning','yellow'), output))
                    answer = input().strip(' ').lower()
                    if answer != 'y':
                        #don't override -> stop
                        print('\nAborted!')
                        sys.exit(1)
                #Export .json file
                if verbose:
                    print('Exporting to %s...' % output)
                with open(output, 'w') as output_file:
                    json.dump(main_module.convert_to_dict(), output_file)
                if verbose:
                    print('Export complete !')

            else:
                pass
                ### COMPILER ###
            
        else:
            #Invalid file format -> 5
            error.ThrowError(5)
    else:
        #Invalid path -> 26
        error.ThrowError(26)
        

    

if __name__ == "__main__":
    main() #pylint: disable=no-value-for-parameter
