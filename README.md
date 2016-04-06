# Jailify/Dejailify

Create or destroy jails for senior project teams on our senior project jail
host.

##Dependencies
`jailify` depends on `python3` being installed.

## Installation
Run ..............

## Example Usage

### `jailify`
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


