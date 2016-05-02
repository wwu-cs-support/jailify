# Jailify/Dejailify

Create or destroy jails for senior project teams on our senior project jail
host.

# Preconditions
1. `jailify` is dependent on a ZFS dataset configured as a base jail that can
    be cloned to create new jails. 
2. `jailify` must have `sendmail` enabled in the jail. This change can be made
   in the base jail that all future jails will be cloned from.
3. `jailify` must have `/usr/share/skel` formatted with an added `.ssh/` and an
   `authorized_keys` file for creation of user accounts to work. This change 
   can also be made in the base jail.
4. `jailify` also is dependent on `python3` being installed.
5. The host must specify an acceptable range of IP addresses for the jails to
   use in `/etc/jail.conf`. You may put this comment anywhere in
   `/etc/jail.conf`. However, we suggest you place it after the `#DEFAULTS`
   section and before the jails. Use the following format:
   ```
   #ip-range = <IP Range>
   ``` 
   `<IP Range>` should be the acceptable IP addresses expressed in CIDR notation,
    such as: `10.10.1.128/25`.
6. `jailify` must have `sudo` installed in the jail. This change can be made
   in the base jail.

# Installation
To install `jailify` run the following command:
```
pip install git+https://gitlab.***REMOVED***/cs-support/jailify.git@master
```

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

### Example Usage

The basic usage is this:
```
dejailify [team_name]
```

With no arguments dejailify should query `/etc/jail.conf` for meta-data
embedded in comments above the jail descriptions to present a list of jails
allocated for destruction.

For example, `jailify` with no argument should look like:
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
With the `team_name` argument `dejailify` might look like:
```
***REMOVED***@***REMOVED***:~ % sudo dejailify redteam
Destroy redteam.***REMOVED***? [y/N] y
[WARNING]: This will destroy ALL jail data for redteam.***REMOVED***. Are you sure? [y/N] y
Destroying redteam.***REMOVED***... done.
***REMOVED***@***REMOVED***.***REMOVED***:~ %
```
