# Jailify

Create jails for senior project groups based on their provided metadata.

## Installation
Run ..............

## Example Usage

### `jailify`
```
myusername@hostname:~ % sudo jailify ./greenteam.tgz

myusername@hostname:~ % sudo jailify ./blueteam
```

### `dejailify`
```
myusername@hostname:~ % sudo dejailify
The following jails are allocated for destruction:
    - blueteam.sr***REMOVED***
    - greenteam.sr***REMOVED***
    - redteam.sr***REMOVED***
Destroy all of them? [y/N] n
Destroy them individually? [y/N] y
Destroy blueteam.***REMOVED***? [y/N] y
[WARNING]: This will destroy ALL jail data for blueteam.***REMOVED***. Are you sure? [y/N] y
Destroying blueteam.***REMOVED***... done.
Destroy greenteam.***REMOVED***? [y/N] n
Destroy redteam.***REMOVED***? [y/N] n

myusername@hostname:~ % sudo dejailify redteam
Destroy redteam.***REMOVED***? [y/N] y
[WARNING]: This will destroy ALL jail data for redteam.***REMOVED***. Are you sure? [y/N] y
Destroying redteam.***REMOVED***... done.
```









extraction.py - The purpose of this program is to extract data from a given tarball or directory. It will
                extract said data package, create a dictionary from the json file and add all of the public keys into the
                corresponding team member's section of the dictionary. The final step is to validate the dictionary that 
                contains all the extracted data.
