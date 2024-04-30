#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KERBAL SAVE VIEWER

Implemented:
- Load .sfs savefile
- Export to JSON
    - Duplicate keys stored in an array

Maybe TODO:
- Export back to .sfs (maybe? duplicate keys will be annoying)
- Tree viewer with Textual TUI

Created on Friday, 26 April 2024 // GPL-3
"""

# --- Information ---
__title__ = 'Kerbal Save Viewer'
__version__ = 202404.29
__author__ = 'IKJ'

# --- Initialise ---
from rich import print         # Print Formatting
import argparse                # Argument Parsing
import itertools               # Duplicate key handling
import json                    # JSON General Handling
import io


# --- Functions ---
# JSON encoding - Handling Duplicates
def _duplicate_object_hook(pairs):
    ''' Allows parsing a JSON with duplicate keys.
        {"key":"value", "key" : "value2"} --> { "key" : ["value", "value2"] }
        https://stackoverflow.com/questions/29203165/dealing-with-json-with-duplicate-keys '''

    def _key(pair):
        (k, v) = pair
        return k

    def gpairs():
        for (k, group) in itertools.groupby(pairs, _key):
            ll = [v for (_, v) in group]
            (v, *extra) = ll
            yield (k, ll if extra else v)

    return dict(gpairs())


# Split a string reference path into a list, and convert any numbers to integers
def _tree_path_split(reference: str, branch: list = ["GAME"]) -> list[str, int]:
    """ Split a path string into a list that can be passed to dict_reference_from_list()"""
    # Split the provided path on / and strip trailing slashes
    path = reference.rstrip('/').split('/')
    # If they ask for everything, let 'em have it
    if path[-1] == 'ALL':
        return branch
    # Convert any numbers to integer type
    for count, step in enumerate(path):
        try:
            path[count] = int(step)
        except ValueError:
            pass
    return branch + path


# Find a specific item from a path, given as a list
def _dict_reference_from_list(data, keys: list):
    """ Recursive function.
        Return a value from a dictionary using a 'path' given as a list."""
    if keys:
        return _dict_reference_from_list(data[keys[0]], keys[1:])
    else:
        return data


# --- SFS Handling ---
def sfs_parse(sfs_file: io.TextIOWrapper | str) -> dict:
    """ Convert an SFS file to a .json-compatible string. Then, parse using json.loads().
        Expects either an opened text file (_io.TextIOWrapper) or string.

        Works with a series of str.replace operations, which is fairly quick.
        The alternative way to do this is to parse the .sfs line-by-line or char-by-char, as in 'sfsutils' by mark9064. """

    # --- Type Checking ---
    if type(sfs_file) == io.TextIOWrapper:
        sfs = sfs_file.read()
    elif type(sfs_file) != str:
        print('Unexpected type passed to sfs_parse()', type(sfs_file))
        return False

    # --- Convert to JSON formatting ---
    # Clean Input String; remove tabs, whitespace at the end of lines
    sfs = sfs.replace("\t", '').replace(" \n", '\n').replace('\n ', '\n')

    # Turn Node names into JSON Object Keys
    sfs = sfs.replace('}\n', '}')      # i.e. Turn
    sfs = sfs.replace('\n{', ':{')     # ...}\nTHING\n{... into
    sfs = sfs.replace('{\n}', '{}\n')  # ...}, {"THING":{...

    # Turn assignemnt (=) into key-value pairs
    sfs = sfs.replace(' =\n', ' = \n')         # Ensure two spaces around assignment to an empty value
    sfs = sfs.replace(' = ', '":"')            # Replace ' = ' with " : "
    sfs = sfs.replace('\n', '",\n"')           # Add double-quotes at the start and end of newlines
    sfs = sfs.replace(':{",', '":{')           # Fix misquoted objects and braces caused by the above
    sfs = sfs.replace(':{}"', '":{}')          #     ''

    for n in range(args.d):            # Fix Dedenting Braces
        i = args.d - n                 # Deepest I can see is 8 or so. default 16 should be plenty
        fr = ',\n"' + ('}' * i)        #    "}}}}} with <i> braces
        to = ('}' * i) + ',\n"'        #    }}}}}" with <i> braces
        sfs = sfs.replace(fr, to)

    # Fix start and end of file to make sure we have valid JSON
    sfs = '{"' + sfs[:-3] + '}'

    # Now that we have a valid json-compatible string, convert it to JSON
    try:
        converted_sfs_file = json.loads(sfs, object_pairs_hook=_duplicate_object_hook)
        return converted_sfs_file
    except json.decoder.JSONDecodeError as d_err:
        print('Unable to convert! Error:')
        print('\t' + repr(d_err) + '\n')
        return False   # Something has Gone Wrong


def sfs_dump():        # TODO
    """ Convert a Dictionary or .json to a .sfs-compatible string"""
    return


# -- Data handling for the imported dictionary
def inspect_data(data: dict, path: str | list):
    if type(path) == str:
        path = _tree_path_split(path)

    return _dict_reference_from_list(data, path)


def retype_data(data, reverse=False):
    # Recursively re-type a dictionary or list, to or from string to the appropriate type
    def _recursive_apply(func, obj):
        """ Recursively apply a given function to all items in a dict or list. """
        if isinstance(obj, dict):      # if dict, apply to each key
            return {k: _recursive_apply(func, v) for k, v in obj.items()}
        elif isinstance(obj, list):    # if list, apply to each element
            return [_recursive_apply(func, elem) for elem in obj]
        else:
            return func(obj)

    def _string_to_object(obj) -> any:
        """ Change a single object's type from string to the appropriate class. """
        # Booleans
        if obj in ('True', 'true'):
            return True
        elif obj in ('False', 'false'):
            return False
        elif obj in ('None', 'none'):
            return None
        # Infinity
        elif obj == 'Infinity':
            return obj
        # Quaternions and Vectors
        try:
            a = []
            for item in obj.split(','):
                a.append(float(item))
            if len(a) == 3 or len(a) == 4:
                return tuple(a)
        except ValueError:
            pass
        # Integers
        try:
            return int(obj)
        except ValueError:
            pass
        # Float and NaN
        try:
            return float(obj)
        except ValueError:
            pass
        # Strings
        return obj

    def _object_to_string(obj) -> any:
        """ Change a single object's type from a Bool, Number, or Tuple back to a string.
        TODO: Convert Lists like SCENARIO [ ... ] back to SCENARIO {}... SCENARIO {}... """
        # Booleans
        if type(obj) == bool:
            return str(obj)
        # Integers, Floats, and Strings
        else:
            return str(obj)

    # Actual Function
    if not reverse:
        return _recursive_apply(_string_to_object, data)
    if reverse:
        return _recursive_apply(_object_to_string, data)


# --- Running as Main ---
if __name__ == '__main__':

    # --- Configuration ---
    # - Command Line Arguments
    argp = argparse.ArgumentParser(
        prog="kerbal_sv",
        description="Convert a KSP save file to JSON",
        epilog=
        "Please note, using -q ALL or -r ALL may lag or crash, because they are very long. -x is not guaranteed to match the input perfectly due to floating point rounding"
    )
    argp.add_argument('filepath', nargs='+', type=argparse.FileType('r'))
    argp.add_argument('-d', metavar='[depth]', action='store', help='change max depth of the input .sfs file', type=int)
    argp.add_argument('-f', '--format', action='store_const', help='format the .json output with indenting and newlines', const=2)
    argp.add_argument('-x', action='store_true', help='recursively interpret non-strings as integers/floats/tuples') # TODO
    argp.add_argument('-t', '--testing', action='store_true', help='output intermediate step to text file (for debugging)')

    printouts = argp.add_argument_group('printouts', 'print an object. use / to get deeper into the tree, and integers for duplicate names.')
    printouts.add_argument('-p', action='append', metavar='[ref/to/obj]', help='print an object inside "PARAMETERS", or ALL')
    printouts.add_argument('-q', action='append', metavar='[ref/to/obj]', help='print an object inside "GAME", or ALL')
    printouts.add_argument('-r', action='append', metavar='[ref/to/obj]', help='print an object inside "FLIGHTSTATE", or ALL')

    # - Defaults
    argp.set_defaults(
        d=16,
        format=None,
        p=[],
        q=[],
        r=[],
        references=[],
        kspv='versionFull',
        testing=False,
        x=False,
    )
    output_name = 'Title'
    output_time = 'persistentTimestamp'

    # - Parse Args
    args = argp.parse_args()
    filepath = args.filepath
    print(args)

    # Assemble a list of paths within the sfs that the user wants to have printed to the screen.
    args.references = []
    for item in args.p:
        args.references.append(_tree_path_split(item, ["GAME", "PARAMETERS"]))
    for item in args.q:
        args.references.append(_tree_path_split(item, ["GAME"]))
    for item in args.r:
        args.references.append(_tree_path_split(item, ["GAME", "FLIGHTSTATE"]))

    # --- Parse and Load File ---
    sfs = args.filepath[0]
    jfs = sfs_parse(sfs)

    if not jfs:        # Fail State
        exit()         # Exit

    if args.x:         # Go through the entire tree and un-stringify all the numbers, constants, and vectors
        jfs = retype_data(jfs)

    # -- Printouts --
    print(f'[bold]{jfs["GAME"][output_name]}[/bold]\n')
    print("Save Time:\t", jfs["GAME"][output_time][0:16].replace("T", " "))
    print("KSP Version:\t", jfs["GAME"][args.kspv], "\n")

    # - User Requested Items -
    for reference in args.references:
        print(reference)
        try:
            print(inspect_data(jfs, reference))
        except KeyError as k_err:
            print("Reference Failed, please check the spelling. This is case sensitive!")

    # -- Output to JSON file --
    with open(filepath[0].name + '.json', 'w') as file:
        file.write(json.dumps(jfs, indent=args.format))
