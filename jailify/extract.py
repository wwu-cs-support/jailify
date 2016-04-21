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
        
        metadata = distribute(pub_keys,metadata)
        return metadata
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
        metadata = distribute(pub_keys, metadata)
        return metadata
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
    pub_keys = {}
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if os.path.basename(file) == "metadata.json":
                with open(os.path.join(subdir,file), 'r') as meta:
                    try:
                        metadata = json.loads(meta.read())
                    except ValueError:
                        raise InvalidJSONError("Error: Could no decode JSON")
            elif os.path.basename(file).endswith(".pub"):
                username = os.path.splitext(file)[0]
                with open(os.path.join(subdir, file), 'r') as key:
                    pub_keys[username] = key.read()

    metadata = distribute(pub_keys, metadata)
    return metadata


## DISTRIBUTE ##
def distribute(pub_keys, metadata):
    """"Takes the public keys contained in pub_keys and distributes them into
         metadata dictionary for each user.

    Args:
        pub_keys (dict): the dictionary containing usernames and public keys.
        metadata (dict): the dictionary containing the extracted metadata.
    Returns:
        metadata (dict): the same metadata as before, but with a new field for
                         each user called "publicKey" & the corresponding key.
    """
    try:
        for k in pub_keys.keys():
            for m in metadata["teamMembers"]:
                if k == m["username"]:
                    pub_keys[k] = pub_keys[k].strip()
                    m["publicKey"] = pub_keys[k]
        return metadata
    except KeyError:
        raise InvalidJSONError("Malformed JSON. Better check that out.")


## VALIDATE ##
def validate(metadata):
    """Validates the keys, hostname, and team member usernames of the metadata
       dictionary. Relies on jailify.extract.REQUIRED_KEYS and
       jailify.extract.REQUIRED_USER_KEYS.

    Args:
        metadata (dict): metadata in dictionary form
    Returns:
        None
    """
    ## validate metadata ##
    if all(k in metadata for k in REQUIRED_KEYS):
        regex = re.compile('^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$')
        match = regex.match(metadata["hostname"])
        if not match:
            raise InvalidHostname("Error: Hostname Invalid");
    else:
        raise InvalidMetadata("Error: Metadata parameters are invalid");
    ## validate team members##
    teamMembers = metadata["teamMembers"]
    for member in teamMembers:
        try:
            if not (all(k in member for k in REQUIRED_USER_KEYS) and
                member["username"] == member["publicKey"].split()[-1]):
                raise ValidationError("Error: Validation Failed")
        except KeyError:
            raise ValidationError("Error: Validation Error - Key Error")

if __name__ == '__main__':
    main(sys.argv)
