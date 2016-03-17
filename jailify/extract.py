#***REMOVED*** | ***REMOVED***@wwu.edu | 04 March 2016
#
#    The purpose of this program is to extract data from a given tarball or directory. 
#  It will extract said data package, create a dictionary from the json file and add
#  all of the public keys into the corresponding team member's section of the dictionary.
#  The final step is to validate the dictionary that contains all the extracted data.

import os
import re
import sys
import json
import tarfile
import zipfile
import os.path
import mimetypes

def main(argv):
    """Check for correct number args, determine file type, extract
       file, extract data from file.

    Args:
        argv (list): first arg should be the file name.
    Returns:
        None
    """

    # Check for correct number of args and get the file name/path.
    if (len(argv) == 2):
        try:
            if os.path.isfile(argv[1]) or os.path.isdir(argv[1]):
                file_name = argv[1]
        except ValueError:
            print("Error with file.")
    else:
        print("Incorrect number of arguments")
        sys.exit()

    #Extract based on the file type returned from determine_file_type
    metadata = extract(determine_file_type(file_name),file_name)

    validate(metadata)


## DETERMINE_FILE_TYPE ##
def determine_file_type(file_name):
    """Determines which type of file is given.

    Args:
        command_line_argument (str): the name of the file given on the command
                                     line.
    Returns:
        file_type (str): aborts if file is not a directory, gzip, zip or xz compressed file.
                         otherwise returns a string representing one of the four types.
    """
    if os.path.isdir(file_name):
        file_type = "dir"
    elif mimetypes.guess_type(file_name)[1] == 'bzip2':
        file_type = "bz2"
    elif mimetypes.guess_type(file_name)[1] == 'gzip':
        file_type = "gz"
    elif zipfile.is_zipfile(file_name):
        file_type = "zip"
    elif mimetypes.guess_type(file_name)[1] == "xz":
        file_type = "xz"
    else:
        print("Type is unacceptable")
        sys.exit()

    return file_type

## EXTRACT ##
def extract(filetype, filename):
    """Determines what type of extraction should be used on the file and calls
       the appropriate extract function. Then returns the directory to be worked
       with.

    Args:
        filetype (str): the type of file. 'dir', 'zip', 'xz', 'bzip2' or 'gzip'.
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
        print("error with file type in extract()")
        sys.exit()
    return mdata

## EXTRACT_TAR ##
def extract_tar(filenametar, comptype):
    """Opens, extracts, and closes tar file that has been compressed with one of gzip, xz, and bzip2.

    Args:
        filenametar (str): the name of the file as provided on the command
                           line.
        comptype    (str): the compression type (bzip2, gzip or xz) to be passed in when decompressing.
    Returns:
        metadata (dict): the json contents and public keys combined into a dictionary.
    """
    get_metadata = False
    pub_keys = {}
    try:
        with tarfile.open(filenametar, 'r:{}'.format(comptype)) as tar:
            for f in tar:
                if os.path.basename(f.name) == "metadata.json":
                    metadata = decode(tar.extractfile(f).read())
                    get_metadata = True
                elif os.path.basename(f.name).endswith('.pub'):
                    username = os.path.splitext(os.path.basename(f.name))[0]
                    key = bytes.decode(tar.extractfile(f).read())
                    pub_keys[username] = key
        for k in pub_keys.keys():
            for m in metadata["teamMembers"]:
                if k == m["username"]:
                    if pub_keys[k].endswith("\n"):
                        pub_keys[k] = pub_keys[k][:-1]
                    m["publicKey"] = pub_keys[k]
        return metadata
    except tarfile.TarError:
        print("Couldn't open tarfile")
        sys.exit()

## EXTRACT_ZIP ##
def extract_zip(zipfilename):
    """Opens, extracts, and closes zip files.

    Args:
        zipfilename (str): the name of the file as provided on the command line.
    Returns:
        metadata (dict): the json contents and public keys in a directory
   """
    pub_keys = {}
    try:
        with zipfile.ZipFile(zipfilename) as myzip:
            for n in myzip.namelist():
                if os.path.basename(n) == "metadata.json":
                    metadata = decode(myzip.open(n).read())
                elif os.path.basename(n).endswith('.pub'):
                    username = os.path.splitext(os.path.basename(n))[0]
                    key = bytes.decode(myzip.open(n).read())
                    pub_keys[username] = key
        for k in pub_keys.keys():
            for m in metadata["teamMembers"]:
                if k == m["username"]:
                    if pub_keys[k].endswith("\n"):
                        pub_keys[k] = pub_keys[k][:-1]
                    m["publicKey"] = pub_keys[k]
        return metadata
    except zipfile.BadZipFile:
       print("Couldn't extract zip file")


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
                meta = open(os.path.join(subdir,file),'r')
                metadata = decode(meta)
                meta.close()
            elif os.path.basename(file).endswith(".pub"):
                username = os.path.splitext(file)[0]
                key = open(os.path.join(subdir, file), 'r')
                pub_keys[username] = key.read()
    for k in pub_keys.keys():
        for m in metadata["teamMembers"]:
            if k == m["username"]:
                if pub_keys[k].endswith("\n"):
                    pub_keys[k] = pub_keys[k][:-1]
                m["publicKey"] = pub_keys[k]
    return metadata

## DECODE ##
def decode(json_file_object):
    """Decodes and extracts contents of the metadata.json file.

    Args:
        json_file_object (File Object): a file is .open()-ed and .read() into this function.
    Returns:
        json.loads(jstr) (dict): the json string read and put into a usable dictionary.
    """
    try:
        if isinstance(json_file_object, bytes):
            jstr = bytes.decode(json_file_object)
        else:
            jstr = json_file_object.read()
        return json.loads(jstr)
    except ValueError:
        print("Decoding JSON has failed")

## VALIDATE ##
def validate(metadata):
    """Validates the keys, hostname, and team member usernames of the metadata dictionary.

    Args:
        metadata (dict): metadata in dictionary form
    Returns:
        None
    """
    ## validate metadata ##
    if all(k in metadata for k in ("projectName","client","hostname","facultyContact","client","teamMembers")):
        regex = re.compile('^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$')
        match = regex.match(metadata["hostname"])
        if match:
            pass
        else:
            print("hostname invalid")
            sys.exit()
    else:
        print("incorrect metadata parameters")
        sys.exit()
    ## validate team members##
    teamMembers = metadata["teamMembers"]
    for member in teamMembers:
        try:
            if (all(k in member for k in ("username","publicKey","email","name")) and
                member["username"] == member["publicKey"].split()[-1]):
                pass
            else:
                print("validation failed")
                sys.exit()
        except KeyError:
            print("validation failed - key error")
            sys.exit()

if __name__ == '__main__':
    main(sys.argv)
