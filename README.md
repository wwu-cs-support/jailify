# Jailify/Dejailify

Create or destroy jails for senior project teams on our senior project jail
host.

# Dependencies
`jailify` depends on `python3` being installed.

# Installation
Run ..............


## `jailify`
`jailify` is the command used to create new jails for senior project teams. The
basic usage is this:
```
jailify project_dir
```
where `jailify` is the name of the command and `project_dir` is the **required**
path to a directory (which could be either a plain directory _or_ a tarball)
containing the SSH public keys for each group member. The `project_dir` also
contains a file which should be called `metadata.json`.

### `metadata.json` Format
Here's example of that JSON file with all required fields

```json
{
  "projectName": "Green Team",
  "hostname": "greenteam",
  "facultyContact": "***REMOVED***",
  "client": "CS Support",
  "teamMembers": [
    {
      "username": "***REMOVED***",
      "name": "***REMOVED***",
      "email": "***REMOVED***@students.wwu.edu"
    },
    {
      "username": "***REMOVED***",
      "name": "***REMOVED***",
      "email": "***REMOVED***@students.wwu.edu"
    },
    {
      "username": "***REMOVED***",
      "name": "***REMOVED***",
      "email": "***REMOVED***"
    },
    {
      "username": "***REMOVED***",
      "name": "***REMOVED***",
      "email": "***REMOVED***@students.wwu.edu"
    }
  ]
}
```

### Example Usage
Example usage of `jailify` might look like
```
***REMOVED***@***REMOVED***:~ % sudo jailify ./greenteam.tgz
```
or
```
***REMOVED***@***REMOVED***:~ % sudo jailify ./blueteam
```
where the directory structure of `greenteam.tgz` or `blueteam` is
something like
```
greenteam
├── ***REMOVED***.pub
├── ***REMOVED***.pub
├── metadata.json
├── ***REMOVED***.pub
└── ***REMOVED***.pub
```

## `dejailify`

`dejailify` will be the command used to destroy old senior project jails.
The basic usage is this:
```
dejailify [team_name]
```

With no arguments dejailify should query `/etc/jail.conf` for meta-data
embedded in comments above the jail descriptions to present a list of jails
allocated for destruction.

With the `team_name` argument `dejailify` might look like
```
***REMOVED***@***REMOVED***:~ % sudo dejailify
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
***REMOVED***@***REMOVED***:~ %
```
or
```
***REMOVED***@***REMOVED***:~ % sudo dejailify redteam
Destroy redteam.***REMOVED***? [y/N] y
[WARNING]: This will destroy ALL jail data for redteam.***REMOVED***. Are you sure? [y/N] y
Destroying redteam.***REMOVED***... done.
***REMOVED***@***REMOVED***.***REMOVED***:~ %
```
