# kerbal-savefile-viewer

## Done:
  - Read KSP .sfs file into a .json file

## Todo:
  - Test more save files to ensure compatibility
  - Make a Viewer
    - editing?
  - Export .json to .sfs?


positional arguments:
  filepath

## Command Line Arguments
### Options
```
  -h, --help       show help message and exit
  -d [depth]       change max depth of the input .sfs file
  -f, --format     format the .json output with indenting and newlines
  -k, --kspv       show the full ksp version
  -t, --testing    output intermediate step to text file (for debugging)
```

### Printouts:
Print an object. Use '/' to get deeper into the tree, and integers for duplicate names.
```
  -p [ref/to/obj]  print an object inside "PARAMETERS", or ALL
  -q [ref/to/obj]  print an object inside "GAME", or ALL
  -r [ref/to/obj]  print an object inside "FLIGHTSTATE", or ALL
```
e.g. `-q EnvInfo`, `-q SCENARIO/5/Moon` or `-r VESSEL/1/ORBIT`.
Please note, using -q ALL or -r ALL may lag or crash, because they are very long.
