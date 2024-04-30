# kerbal-savefile-viewer

## Done:
  - Read KSP .sfs file into a python dictionary
  - export dictionary as .json file
  - interpret .sfs file strings as ints, floats, tuples, or booleans
  - return ints, floats, tuples, or booleans to strings
  - reference a given item with `inspect_data(['ref', 'to', 'obj'], data)` or `inspect_data("ref/to/obj", data)`.

## Todo:
  - Test more save files to ensure compatibility
  - Make a Viewer
    - editing?
  - Export .json to .sfs?

## Methods
uh, todo


## Command Line Arguments
### Positional Arguments:
```
  filepath
```

### Options:
```
  -h, --help       show this help message and exit
  -d [depth]       change max depth of the input .sfs file
  -f, --format     format the .json output with indenting and newlines
  -x               recursively interpret non-strings as integers/floats/tuples
  -t, --testing    output intermediate string to text file, before json encoding (debug)
```
Using `-x` means the output is not guaranteed to match the input, due to floating point rounding.

### Printouts:
Print an object. Use '/' to get deeper into the tree, and integers for duplicate names.
```
  -p [ref/to/obj]  print an object inside "PARAMETERS", or ALL
  -q [ref/to/obj]  print an object inside "GAME", or ALL
  -r [ref/to/obj]  print an object inside "FLIGHTSTATE", or ALL
```
e.g. `-q EnvInfo`, `-q SCENARIO/5/Moon` or `-r VESSEL/1/ORBIT`.  
i.e. `-p DIFFICULTY` is equivalent to `-q PARAMETERS/DIFFICULTY`.  
Please note, using `-q ALL` or `-r ALL` may lag or crash, as they can get very long.
