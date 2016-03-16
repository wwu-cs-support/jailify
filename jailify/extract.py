#***REMOVED*** | ***REMOVED***@wwu.edu | 04 March 2016
#
#    The purpose of this program is to determine the file type of a given
# directory or archive and then extract the archive. It will also pull
# out the team name from the title of the directory/archive.

import os
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
        argv (str): first arg should be the file name.
    Returns:
        None
    """
    print()
    # Check for correct number of args and get team name.
    if (len(sys.argv) == 2):
        file_name = argv[1]
        print("file_name set to: " + file_name)
        team_name = check_title(file_name)
        print("team_name set to: " + team_name)
    else:
        print("Incorrect number of arguments")
        sys.exit()

    # Determine and return the file type.
    file_type = inspect_file(file_name)
    print("file_type is: " + file_type + " in main")

    # Extract based on file type
    extract(file_type, file_name)




def check_title(filename):
    """Retrieves the password from the name of the file.

    Args:
        filename (str): name of the file including file extension
    Returns:
        teamname (str): name of the team, which is file name minus the file
                        extension
    """
    print("command line argument sent to check_title")
    if os.path.isfile(filename) or os.path.isdir(filename):
        teamname = os.path.splitext(filename)[0]
        return teamname
    else:
        print("file not found")
        sys.exit()

def inspect_file(command_line_argument):
    """Determines which type of file is given.

    Args:
        command_line_argument (str): the name of the file given on the command
                                     line.
    Returns:
        file_type (str): aborts if file is not a directory, gzip, zip or xz compressed file.
                         otherwise returns a string representing one of the four types.
    """
    print("team_name sent to inspect_file. Let's find the type.")
    if os.path.isdir(command_line_argument):
        file_type = "dir"
        print("file_type set to: " + file_type)
    elif mimetypes.guess_type(command_line_argument)[1] == 'bzip2':
        file_type = "bz2"
        print("file_type set to: " + file_type)
    elif mimetypes.guess_type(command_line_argument)[1] == 'gzip':
        file_type = "gz"
        print("file_type set to: " + file_type)
    elif zipfile.is_zipfile(command_line_argument):
        file_type = "zip"
        print("file_type set to: " + file_type)
    elif mimetypes.guess_type(command_line_argument)[1] == "xz":
        file_type = "xz"
        print("file_type set to: " + file_type)
    else:
        print("Type is unacceptable")
        sys.exit()

    return file_type


def extract(filetype, filename):
    """Determines what type of extraction should be used on the file and calls
       the appropriate extract function. Then returns the directory to be worked
       with.

    Args:
        filetype (str): the type of file. 'dir', 'zip', 'xz', 'bzip2' or 'gzip'.
        filename (str): the name of the file as provided from the command line.
                        Includes file extension.
    Returns:
        filelist (list): a list containing extracted file objects from the directory.
    """

    if filetype == "bz2" or filetype == "gz" or filetype == "xz":
        print("since file type is " + filetype + "call extract_tar")
        extract_tar(filename, filetype)
    elif filetype == "zip":
        print("since file type is " + filetype + "call extract_tar")
        extract_zip(filename)
    elif filetype == "dir":
        print("Deal with directory")
    else:
        print("error with file type in extract()")
        sys.exit()



### Extraction Functions ###


def extract_tar(filenametar, comptype):
    """Opens, extracts, and closes tar file that has been compressed with one of gzip, xz, and bzip2.

    Args:
        filenametar (str): the name of the file as provided on the command 
                           line.
        comptype    (str): the compression type (bzip2, gzip or xz) to be passed in when decompressing.
    Returns:
        L (list): the members as a list of TarExFile objects.
    """
    get_metadata = False
    print("Parsing through the contents of the archive:")
    try:
        with tarfile.open(filenametar, 'r:{}'.format(comptype)) as tar: 
            for f in tar:
                if os.path.basename(f.name) == "metadata.json":
                    decode(tar.extractfile(f))
                    get_metadata = True
                elif os.path.basename(f.name).endswith('.pub'):
                    print(".pub")
    except tarfile.TarError:
        print("Couldn't open tarfile")




def decode(json_file_object):
    """Decodes and extracts contents of the metadata.json file.

    Args:
        json_file_object (???): the extracted metadata.json file object.
    Returns:
        None
    """
    print("JSON file object sent to decode()")
    try:
        json_contents_in_dictionary = json.JSONDecoder(json_file_object)
        print("json contents:")
        print(json_contents_in_dictionary)
    except json.JSONDecodeError():
        print("Unable to decode json file object")
        sys.exit()
























def extract_zip(zipfilename):
    """Opens, extracts, and closes zip files.

    Args:
        zipfilename (str): the name of the file as provided on the command line.
    Returns:
        L (list): the members of the archive extracted as file objects.
   """
    try:
        L = []
        with zipfile.ZipFile(zipfilename) as myzip:
            for n in myzip.namelist():
                L.append(myzip.open(n))
    except zipfile.BadZipFile:
       print("Couldn't extract zip file")

if __name__ == '__main__':
    main(sys.argv)
