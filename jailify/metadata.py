#***REMOVED*** | ***REMOVED***@wwu.edu | 04 March 2016
#
#    The purpose of this program is to extract data from a given tarball or
#  directory. It will extract said data package, create a dictionary from the
#  json file and add all of the public keys into the corresponding team
#  member's section of the dictionary. The final step is to validate the
#  dictionary that contains all the extracted data.

import os
import re
import sys
import json
import magic
import tarfile
import zipfile
import os.path
import tempfile
import mimetypes
import subprocess
from subprocess import DEVNULL, CalledProcessError

REQUIRED_KEYS = ("projectName","client","hostname","facultyContact","teamMembers")
REQUIRED_USER_KEYS = ("username","email","name")

class ExtractionError(Exception):
    """An exception that is raised when the file type is invalid.

    Args:
        message (str): an error message

    Attributes:
        message (str): an error message
    """
    def __init__(self, message):
        self.message = message


class InvalidFileType(ExtractionError):
    """An exception that is raised when an invalid file type is given."""
    pass


class FailedToExtractFile(ExtractionError):
    """An exception that is raised when jailify fails to extract the given file."""
    pass


class ExtraneousPublicKey(ExtractionError):
    """An exception that is raised when jailify finds more public keys than team members."""
    pass


class InvalidJSONError(ExtractionError):
    """An exception that is raised when there is invalid JSON present."""
    pass


class ValidationError(ExtractionError):
    """An exception that is raised when there is an error with SSH key validation."""
    pass


class InvalidHostname(ExtractionError):
    """An exception that is raised when there is an error with the given hostname."""
    pass


class InvalidMetadata(ExtractionError):
    """An exception that is raised when there is an error with the given metadata."""
    pass


## DETERMINE_FILE_TYPE ##
def determine_file_type(file_name):
    """Determines which type of file is given.

    Args:
        file_name (str): the name of the file given on the command
                         line.
    Returns:
        file_type (str): aborts if file is not a directory, gzip, zip or xz
                         compressed file. Otherwise returns a string
                         representing one of the four types.
    """
    if os.path.isdir(file_name):
        file_type = 'dir'
    else:
        fmag = magic.Magic(magic.MAGIC_NONE)
        magic_type = fmag.from_file(file_name)

        if magic_type[:5] == 'POSIX':
            file_type = 'tar'
        elif magic_type[:5] == 'bzip2':
            file_type = 'bz2'
        elif magic_type[:4] == 'gzip':
            file_type = 'gz'
        elif magic_type[:3] == 'Zip':
            file_type = 'zip'
        elif magic_type[:2] == 'XZ':
            file_type = 'xz'
        else:
            raise InvalidFileType("{} is an invalid file type".format(magic_type))
    return file_type


## EXTRACT_TAR ##
def extract_tar(tar_path, comp_type):
    """Opens, extracts, and closes tar file that has been compressed with one
       of gzip, xz, and bzip2.

    Args:
        tar_path (str): The path to the tar file.
        comp_type    (str): the compression type (bzip2, gzip or xz) to be
                           passed in when decompressing.

    Returns:
        directory (str): The path to the extracted (or un-tarred)  directory.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        if tarfile.is_tarfile(tar_path):
            with tarfile.open(tar_path, 'r{}'.format(":" + comp_type if comp_type in ("bz2", "gz", "xz") else "")) as tf:
                paths = []
                for member in tf.getmembers():
                    paths.append(os.path.join(temp_dir, member.path))
                    tf.extract(member, path=temp_dir)
                metapath = paths[0]
                return metapath if os.path.isdir(metapath) else os.path.dirname(metapath)
        elif comp_type is "gz":
            cmd = ["tar", "-xzvf", tar_path, "-C", temp_dir]
            subprocess.run(cmd, stdout=DEVNULL, stderr=DEVNULL, check=True)
            return os.path.join(temp_dir, tar_path.split('.')[0])
        else:
            raise FailedToExtractFile("{} is not readable".format(tar_path))
    except (FileNotFoundError, PermissionError, tarfile.TarError):
        raise FailedToExtractFile("{} does not exist, or is malformed".format(tar_path))


## EXTRACT_ZIP ##
def extract_zip(zip_path):
    """Opens, extracts, and closes zip files.

    Args:
        zip_path (str): The path to the zip file.

    Returns:
        directory (str): The path to the unzipped directory.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            valid_files = (n for n in zf.namelist() if n.endswith('.json') or n.endswith('.pub'))
            paths = [zf.extract(m, path=temp_dir) for m in valid_files]
            return os.path.dirname(paths[0])
    except (FileNotFoundError, PermissionError, zipfile.BadZipFile, zipfile.LargeZipFile):
        raise FailedToExtractFile("{} does not exist, is not readable, or is malformed".format(zip_path))


## VALIDATE ##
def validate_metadata(metadata):
    """
    Validates the metadata by verifying that its keys match
    ``jailify.extract.REQUIRED_KEYS``.

    Args:
        metadata (dict): metadata in dictionary form

    Returns:
        None
    """
    ## validate metadata ##
    if all(key in metadata for key in REQUIRED_KEYS):
        regex = re.compile('^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$')
        match = regex.match(metadata["hostname"])
        if not match:
            raise InvalidHostname("invalid hostname")
    else:
        raise InvalidMetadata("invalid metadata")


def validate_team_members(team_members):
    """
    Validates the team member dictionaries in a ``team_members`` list by
    verifying that each team member's keys match
    ``jailify.extract.REQUIRED_USER_KEYS``.

    Args:
        team_members (list): a list of team member dictionaries

    Returns:
        None
    """
    if team_members:
        for member in team_members:
            try:
                if not (all(key in member for key in REQUIRED_USER_KEYS)):
                    raise ValidationError("team member validation failed")
            except KeyError:
                raise ValidationError("key error in team member validation")
    else:
        raise ValidationError("team member list is empty")


def valid_ssh_key(path):
    command = ('/usr/bin/ssh-keygen', '-lf', path)
    try:
        subprocess.run(command, stdout=DEVNULL, stderr=DEVNULL, check=True)
        return True
    except CalledProcessError:
        return False


## BUID_METADATA ##
def build_metadata(directory):
    """Retrieves desired metadata and public keys from directory.

    Args:
        directory (str): name of directory
    Returns:
        metadata (dict): the json contents and public keys in a dictionary.
    """
    try:
        with open(os.path.join(directory, "metadata.json"), "r") as f:
            try:
                metadata = json.load(f)
            except ValueError:
                raise InvalidJSONError("malformed metadata.json")
            # Validate top-level JSON. Let exceptions bubble up.
            validate_metadata(metadata)

            team_members = metadata['teamMembers']

            # Validate team member fields. Let exceptions bubble up.
            validate_team_members(team_members)

            if len(os.listdir(directory)) != (len(team_members) + 1):
                raise ExtraneousPublicKey("team members do not match public keys")

            for member in team_members:
                username = member['username']
                pub_path = os.path.join(directory, "{}.pub".format(username))

                try:
                    # Reading in the key before validating it allows us to find out if it's a private key.
                    with open(pub_path, 'r') as pub_file:
                        member['publicKey'] = pub_file.read().rstrip('\n')

                        if 'PRIVATE KEY' in member['publicKey']:
                            raise ValidationError("found private key for {} (╯°□°）╯︵ ┻━┻".format(username))
                except FileNotFoundError:
                    raise FailedToExtractFile("missing public key for {}".format(username))

                if not valid_ssh_key(pub_path):
                    raise ValidationError("invalid SSH key for {}".format(username))

            return metadata
    except FileNotFoundError:
        raise FailedToExtractFile("metadata.json does not exist")


## GET_METADATA ##
def get_metadata(file_type, filename):
    """Determines what type of extraction should be used on the file and calls
       the appropriate extract function. Then returns the directory to be
       worked with.

    Args:
        file_type (str): the type of file. 'dir', 'zip', 'xz', 'bzip2' or 'gzip'
        filename (str): the name of the file as provided from the command line.
                        Includes file extension.
    Returns:
        mdata (dict): the dictionary containig all metadata
    """
    if file_type in ("tar", "bz2", "gz", "xz"):
        path = extract_tar(filename, file_type)
    elif file_type == "zip":
        path = extract_zip(filename)
    elif file_type == "dir":
        path = filename
    else:
        raise FailedToExtractFile("could not extract data from {}".format(filename))
    return build_metadata(path)
