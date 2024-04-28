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
from rich import print         # Formatting
from datetime import datetime  # Formatting Datetime
import json                    # JSON General Handling
from itertools import groupby  # Used for JSON duplicate key handling

# - Config
debug_output_name = "Title"
debug_output_time = "persistentTimestamp"
debug_output_vers = "version"


# JSON Encoding - Duplicate Pairs
def duplicate_object_pairs_hook(pairs):
    """
    Allows parsing a JSON with duplicate keys.
    {"key":"value", "key" : "value2"} --> { "key" : ["value", "value2"] }
    
    https://stackoverflow.com/questions/29203165/dealing-with-json-with-duplicate-keys"""

    def _key(pair):
        (k, v) = pair
        return k

    def gpairs():
        for (k, group) in groupby(pairs, _key):
            ll = [v for (_, v) in group]
            (v, *extra) = ll
            yield (k, ll if extra else v)

    return dict(gpairs())


# --- File Load ---
filepath = '/home/ikj/Projects/python/data/persistent.sfs'
with open(filepath, 'r') as file:
    sfs = file.read()

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

for n in range(16):            # Fix Dedenting Braces
    i = 10 - n                 # I really hope nothing ever goes this deep. Deepest I can see is 8 or so.
    fr = ',\n"' + ('}' * i)    # "}}}}} with i braces
    to = ('}' * i) + ',\n"'    # }}}}}" with i braces
    sfs = sfs.replace(fr, to)

# Fix start and end of file to make sure we have valid JSON
sfs = '{"' + sfs[:-3] + '}'

# --- Output ---
# - Output munged string to TXT file for Debugging
with open(filepath + '.debug.json', 'w') as file:
    file.write(sfs)

# - Read string as JSON
jfs = json.loads(sfs, object_pairs_hook=duplicate_object_pairs_hook)
# Printout to confirm it worked

print(f'\n------\n [bold]{jfs["GAME"][debug_output_name]}[/bold]\n------\n')
print("Save Time:\t", jfs["GAME"][debug_output_time][0:16].replace("T", " "))
print("KSP Version:\t", jfs["GAME"][debug_output_vers], "\n")

# - Output to JSON file
with open(filepath + '.json', 'w') as file:
    file.write(json.dumps(jfs, indent=2))
