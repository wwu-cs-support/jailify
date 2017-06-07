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
4. `jailify` is dependent on `python3` being installed.
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
pip install git+https://github.com/wwu-cs-support/jailify.git@master
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
  "facultyContact": "Jane Smith",
  "client": "CS Support",
  "teamMembers": [
    {
      "username": "rossb",
      "name": "Bob Ross",
      "email": "rossb@example.com"
    },
    {
      "username": "doej",
      "name": "Jane Doe",
      "email": "doej@example.com"
    },
    {
      "username": "cohenh",
      "name": "Harriet Cohen",
      "email": "cohenh@example.com"
    },
    {
      "username": "obamab",
      "name": "Barack Obama",
      "email": "obamab@example.com"
    }
  ]
}
```

### Example Usage
Example usage of `jailify` might look like
```
user@jailhost:~ % sudo jailify ./greenteam.tgz
```
or
```
user@jailhost:~ % sudo jailify ./blueteam
```
where the directory structure of `greenteam.tgz` or `blueteam` looks like
```
greenteam
├── rossb.pub
├── doe.pub
├── metadata.json
├── cohenh.pub
└── obamab.pub
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
user@jailhost:~ % sudo dejailify
The following jails are allocated for destruction:
    - blueteam.generic-domain
    - greenteam.generic-domain
    - redteam.generic-domain
Destroy all of them? [y/N] n
Destroy them individually? [y/N] y
Destroy blueteam.generic-domain? [y/N] y
[WARNING]: This will destroy ALL jail data for blueteam.generic-domain. Are you sure? [y/N] y
Destroying blueteam... done.
Destroy greenteam? [y/N] n
Destroy redteam? [y/N] n
user@jailhost:~ %
```
With the `team_name` argument `dejailify` might look like:
```
user@jailhost:~ % sudo dejailify redteam
Destroy redteam.generic-domain? [y/N] y
[WARNING]: This will destroy ALL jail data for redteam.generic-domain. Are you sure? [y/N] y
Destroying redteam.generic-domain... done.
user@jailhost.generic-domain:~ %
```
