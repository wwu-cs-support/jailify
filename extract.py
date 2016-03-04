# ***REMOVED*** | ***REMOVED***@wwu.edu | 25 February 2016
#
#    The purpose of this program is to determine the file type of a given
# directory or archive and then extract the archive. It will also pull
# out the team name from the title of the directory/archive.

import os
import sys
import tarfile
import zipfile
import mimetypes
#import os.path

def main(argv):

    # Check for correct number of args and get team name.
    if (len(sys.argv) == 2):
        team_name = check_title(argv[1])
    else:
        print("Incorrect number of arguments")
        sys.exit()

    # Determine and return the file type.
    file_type = inspect_file(sys.argv[1])

    # Extract based on file type
    extract(file_type, argv[1])



##Functions##



def check_title(filename):
    """
    Retrieves the password from the name of the file.

    Args:
        filename(str) - Name of the file including file extension
    Returns:
        teamname(str) - Name of the team, which is file name minus the file extension
    """
    teamname = os.path.splitext(filename)[0]
    return teamname


def inspect_file(command_line_argument):
    """
    Determines which type of file is given.

    Args:
        command_line_argument(str) - The name of the file given on the command line.
    Returns:
        type(str) - Aborts if file is not 'dir', 'tar', 'zip' or 'lzma', otherwise returns one of these types.
    """
    if os.path.isdir(command_line_argument):
        type = "dir"
    elif tarfile.is_tarfile(command_line_argument):
        type = "tar"
    elif zipfile.is_zipfile(command_line_argument):
        type = "zip"
    elif mimetypes.guess_type(command_line_argument) == "lzma":
        type = "lzma"
    else:
        print("Type is unacceptable")
        sys.exit()

    return type


def extract(filetype, filename):
    """
    Determines what type of extraction should be used on the file and calls the appropriate extract function.

    Args:
        filetype(str) - The type of file. 'dir', 'zip', 'lzma' or 'tar'.
        filename(str) - The name of the file as provided from the command line. Will include file extension.
    Returns:
        None
    """
    if filetype == "tar":
        extract_tar(filename)
    elif filetype == "zip":
        extract_zip(filename)
    elif filetype == "lzma":
        extract_lzma(filename)
    else:
        print("it's a directory")


### Extraction Functions ###


def extract_tar(filenametar):
    """
    Opens, extracts, and closes tar file.

    Args:
        filenametar(str) - the name of the file as provided on the command line.
    Returns:
        None
    """
    try:
        tar = tarfile.open(filenametar)
        tar.extractall()
        tar.close()
    except tarfile.TarError:
        print("Couldn't open tarfile")


def extract_lzma(lzfile):
    """
    Extracts lzma compressed files.

    Args:
        lzfile(str) - the name of the file as provided on the command line.
    Returns:
        None
    """
    try:
        lz = tarfile.open(lzfile, 'r:xz')
        lz.extractall()
        lz.close()
    except tarfile.TarError:
        print("LZMA extraction error")



#def extract_zip(zipfile):
#    """
#    Opens, extracts, and closes zip files.
#
#    Args:
#        zipfile(str) - the name of the file as provided on the command line.
#    Returns:
#        None
#   """
#    try:
#        zipfile.open()
#        zipfile.extractall()
#        zipfile.close()
#    except zipfile.BadZipFile:
#       print("Couldn't extract zip file")
        








if __name__ == '__main__':
    main(sys.argv)
