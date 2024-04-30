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
__version__ = 202404.28
__author__ = 'IKJ'

# --- Initialise ---

import argparse        # Argument Parsing
import itertools       # Duplicate key handling
import json            # JSON General Handling

from rich import print         # Print Formatting


# --- Functions ---
# JSON Encoding - Duplicate Pairs
def duplicate_object_pairs_hook(pairs):
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
def treepath_split(reference: str, branch: list = ["GAME"]) -> list[str, int]:
    """Split a path string into a list that can be passed to dictionary_reference_from_list()"""
    # Split the provided path on / and strip trailing
    path = reference.rstrip('/').split('/')

    # If they ask for everything, let 'em have it
    if path[-1] == 'ALL':
        return branch

    # Convert any numbers into integer type
    for count, step in enumerate(path):
        try:
            path[count] = int(step)
        except ValueError:
            pass

    return branch + path


# Find a specific item from a path given as a list
def dictionary_reference_from_list(data, keys: list):
    """Recursive function. Return a value from a dictionary using a path given as a list."""
    if keys:
        return dictionary_reference_from_list(data[keys[0]], keys[1:])
    else:
        return data


# --- Configuration ---
# - Command Line Arguments
argp = argparse.ArgumentParser(prog="kerbal_sv",
                                description="Convert a KSP save file to JSON",
                                epilog="Please note, using -q ALL or -r ALL may lag or crash, because they are very long.")
argp.add_argument('filepath', nargs='+', type=argparse.FileType('r'))
argp.add_argument('-d', metavar='[depth]', action='store', help='change max depth of the input .sfs file', type=int)
argp.add_argument('-f', '--format', action='store_const', help='format the .json output with indenting and newlines', const=2)
argp.add_argument('-k', '--kspv', action='store_const', help='show the full ksp version', const="versionFull")
argp.add_argument('-t', '--testing', action='store_true', help='output intermediate step to text file (for debugging)')

printouts = argp.add_argument_group('printouts', 'print an object. use / to get deeper into the tree, and integers for duplicate names.')
printouts.add_argument('-p', action='append', metavar='[ref/to/obj]', help='print an object inside "PARAMETERS", or ALL')
printouts.add_argument('-q', action='append', metavar='[ref/to/obj]', help='print an object inside "GAME", or ALL')
printouts.add_argument('-r', action='append', metavar='[ref/to/obj]', help='print an object inside "FLIGHTSTATE", or ALL')

# - Defaults
argp.set_defaults(d=16, format=False, p=[], q=[], r=[], kspv='version', testing=False)
output_name = 'Title'
output_time = 'persistentTimestamp'

# - Parsing
args = argp.parse_args()
filepath = args.filepath

# Assemble a list of paths within the sfs that the user wants to have printed to the screen.
printout_paths = []
for item in args.p:
    printout_paths.append(treepath_split(item, ["GAME", "PARAMETERS"]))

for item in args.q:
    printout_paths.append(treepath_split(item, ["GAME"]))

for item in args.r:
    printout_paths.append(treepath_split(item, ["GAME", "FLIGHTSTATE"]))

print(args)
print(printout_paths)

# --- File Load ---
sfs = args.filepath[0].read()

# --- Convert to JSON formatting ---
# Clean Input String of tabs and whitspace at the end of lines
sfs = sfs.replace("\t", '').replace(" \n", '\n').replace('\n ', '\n')

# Turn Node names into JSON Object Keys
sfs = sfs.replace('}\n', '}')          # i.e. Turn
sfs = sfs.replace('\n{', ':{')         # ...}\nTHING\n{... into
sfs = sfs.replace('{\n}', '{}\n')      # ...}, {"THING":{...

# Turn assignemnt (=) into key-value pairs
sfs = sfs.replace(' =\n', ' = \n')     # Ensure two spaces around assignment to an empty value
sfs = sfs.replace(' = ', '":"')        # Replace ' = ' with " : "
sfs = sfs.replace('\n', '",\n"')       # Add double-quotes at the start and end of newlines
sfs = sfs.replace(':{",', '":{')       # Fix misquoted objects and braces caused by the above
sfs = sfs.replace(':{}"', '":{}')      #     ''

for n in range(args.d):        # Fix Dedenting Braces
    i = args.d - n             # Deepest I can see is 8 or so. default 16 should be plenty
    fr = ',\n"' + ('}' * i)    #    "}}}}} with <i> braces
    to = ('}' * i) + ',\n"'    #    }}}}}" with <i> braces
    sfs = sfs.replace(fr, to)

# Fix start and end of file to make sure we have valid JSON
sfs = '{"' + sfs[:-3] + '}'

# --- Output ---
# - Debug - Output munged string to TXT file for Debugging
if args.testing:
    with open(filepath + '.debug.json', 'w') as file:
        file.write(sfs)

# - Read string as JSON
jfs = json.loads(sfs, object_pairs_hook=duplicate_object_pairs_hook)
# Printout to confirm it worked

print(f'[bold]{jfs["GAME"][output_name]}[/bold]\n')
print("Save Time:\t", jfs["GAME"][output_time][0:16].replace("T", " "))
print("KSP Version:\t", jfs["GAME"][args.kspv], "\n")

# Printing a specific item
for reference in printout_paths:
    print(reference)
    try:
        print(dictionary_reference_from_list(jfs, reference))
    except KeyError as k_err:
        print("Reference Failed, please check the spelling. This is case sensitive!")

# - Output to JSON file
with open(filepath[0].name + '.json', 'w') as file:
    file.write(json.dumps(jfs, indent=args.format))
