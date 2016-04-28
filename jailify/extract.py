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
import mimetypes

REQUIRED_KEYS = ("projectName","client","hostname","facultyContact","client","teamMembers")
REQUIRED_USER_KEYS = ("username","publicKey","email","name")

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
        magic_type = magic.from_file(file_name).decode('utf-8')

        if magic_type[:5] == 'bzip2':
            file_type = 'bz2'
        elif magic_type[:4] == 'gzip':
            file_type = 'gz'
        elif zipfile.is_zipfile(file_name):
            file_type = 'zip'
        elif magic_type[:2] == 'XZ':
            file_type = 'xz'
        else:
            raise InvalidFileType("Error: {} is an invalid file type.".format(mime_type)) 
    return file_type


## EXTRACT ##
def extract(filetype, filename):
    """Determines what type of extraction should be used on the file and calls
       the appropriate extract function. Then returns the directory to be 
       worked with.

    Args:
        filetype (str): the type of file. 'dir', 'zip', 'xz', 'bzip2' or 'gzip'
        filename (str): the name of the file as provided from the command line.
                        Includes file extension.
    Returns:
        mdata (dict): the dictionary containig all metadata
    """
    if filetype == "bz2" or filetype == "gz" or filetype == "xz":
        mdata = extract_tar(filename, filetype)
    elif filetype == "zip":
        mdata = extract_zip(filename)
    elif filetype == "dir":
        mdata = extract_dir(filename)
    else:
        raise FailedToExtractFile("Error: Could not extract data from {}.".format(filename))    
    return mdata


## EXTRACT_TAR ##
def extract_tar(filenametar, comptype):
    """Opens, extracts, and closes tar file that has been compressed with one
       of gzip, xz, and bzip2.

    Args:
        filenametar (str): the name of the file as provided on the command
                           line.
        comptype    (str): the compression type (bzip2, gzip or xz) to be
                           passed in when decompressing.
    Returns:
        metadata (dict): the json contents and public keys combined into a
                         dictionary.
    """
    pub_keys = {}
    metadata = {}
    try:
        with tarfile.open(filenametar, 'r:{}'.format(comptype)) as tar:
            for f in tar:
                if os.path.basename(f.name) == "metadata.json":
                    try:
                        metadata = json.loads(bytes.decode(tar.extractfile(f).read()))
                    except ValueError:
                        raise InvalidJsonException("Error: Decoding JSON has failed")
                elif os.path.basename(f.name).endswith('.pub'):
                    username = os.path.splitext(os.path.basename(f.name))[0]
                    key = bytes.decode(tar.extractfile(f).read())
                    pub_keys[username] = key

        if metadata:     
            metadata = distribute(pub_keys,metadata)
            return metadata
        else:
            raise FailedToExtractFile("Error: metadata.json does not exist")

    except tarfile.TarError:
        raise FailedToExtractFile("Error: Failed to extract the tar file")


## EXTRACT_ZIP ##
def extract_zip(zipfilename):
    """Opens, extracts, and closes zip files.

    Args:
        zipfilename (str): the name of the file
    Returns:
        metadata (dict): the json contents and public keys in a directory
   """
    pub_keys = {}
    metadata = {}
    try:
        with zipfile.ZipFile(zipfilename) as myzip:
            for n in myzip.namelist():
                if os.path.basename(n) == "metadata.json":
                    try:
                        metadata = json.loads(bytes.decode(myzip.open(n).read()))
                    except ValueError:
                        raise InvalidJSONError("Error decoding json failed")
                elif os.path.basename(n).endswith('.pub'):
                    username = os.path.splitext(os.path.basename(n))[0]
                    key = bytes.decode(myzip.open(n).read())
                    pub_keys[username] = key
        
        if metadata:
            metadata = distribute(pub_keys, metadata)
            return metadata
        else:
            raise FailedToExtractFile("Error: metadata.json does not exist")

    except zipfile.BadZipFile:
        raise FailedToExtractFile("Error: Failed to extract the zip file")


## EXTRACT_DIR ##
def extract_dir(directory):
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
                raise InvalidJSONError("Error: Malformed metadata.json.")
            # Validate top-level JSON. Let exceptions bubble up.
            validate_metadata(metadata)

            team_members = metadata['teamMembers']

            # Validate team member fields. Let exceptions bubble up.
            validate_team_members(team_members)

            if len(os.listdir(directory)) != len(team_members + 1):
                raise ExtraneousPublicKey("Error: Team members do not match public keys.")

            for member in team_members:
                username = member['username']
                pub_path = os.path.join(directory, "{}.pub".format(username))
                try:
                    with open(pub_path, "r") as pub_file:
                        member['publicKey'] = pub_file.read().rstrip('\n')
                except FileNotFoundError:
                    raise FailedToExtractFile("Error: Missing public key for {}.".format(username))

    except FileNotFoundError:
        raise FailedToExtractFile("Error: metadata.json does not exist.")


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
            raise InvalidHostname("Error: Hostname Invalid")
    else:
        raise InvalidMetadata("Error: Metadata parameters are invalid")


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
                    raise ValidationError("Error: Validation failed.")
            except KeyError:
                raise ValidationError("Error: Validation error - key error")
    else:
        raise ValidationError("Error: Team member list is empty.")
