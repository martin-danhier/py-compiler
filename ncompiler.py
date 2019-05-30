import json
import click
import os
import sys
from noke import error, nobject
from termcolor import colored
from colorama import init


@click.command()
@click.argument('source_file')
@click.option('--output', '-o', type=str, help='Output file. (Default <source_file>.<type_extension>)')
@click.option('--target', '-t', type=str, help='Target format for output file.')
@click.option('--verbose/--silent', '-v/-s', help='Enable/Disable logs. (Default off)')
@click.option('--override/--ask', '-o/-a', help='Enable/Disable the "always override" mode. (Default off)')
def main(source_file, target, output, verbose, override):
    init()  # allow coloring on windows
    if os.path.isfile(source_file):
        if len(source_file) > 4 and source_file[-4:] == '.idk':
            try:
                # Open and read the file
                with open(source_file, 'r') as src:
                    source = src.read()
            except:
                # Unable to open file -> 3
                error.ThrowError(3)

            ### PARSER ###
            if verbose:
                print('Parsing %s...' % source_file)
            main_module = nobject.Module((source, source_file))

            ### PRE INTERPRETER ###
            if target == 'interpret':
                # Check if the output file is valid.
                if output == None:
                    output = source_file[:-4] + '.json'
                # Export .json file
                if verbose:
                    print('Exporting to %s...' % output)
                with open(output, 'w') as output_file:
                    json.dump(main_module.convert_to_dict(), output_file)
                if verbose:
                    print('Export complete !')
            elif target == 'mips':
                # Check if the output file is valid.
                if output == None:
                    output = source_file[:-4] + '.asm'
                print("Exporting to %s..." % output)
                with open(output, 'w') as output_file:
                    output_file.write(main_module.convert_to_mips())
                if verbose:
                    print('Export complete !')
            else:
                pass
                ### COMPILER ###

        else:
            # Invalid file format -> 5
            error.ThrowError(5)
    else:
        # Invalid path -> 26
        error.ThrowError(26)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
