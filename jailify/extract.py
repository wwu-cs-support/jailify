#***REMOVED*** | ***REMOVED***@wwu.edu | 04 March 2016
#
#    The purpose of this program is to determine the file type of a given
# directory or archive and then extract the archive. It will also pull
# out the team name from the title of the directory/archive.

import os
import sys
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

    # Check for correct number of args and get team name.
    if (len(sys.argv) == 2):
        file_name = argv[1]
        team_name = check_title(file_name)
    else:
        print("Incorrect number of arguments")
        sys.exit()

    # Determine and return the file type.
    file_type = inspect_file(file_name)
	
    # Extract based on file type
    file_contents = extract(file_type, file_name)
    print(file_contents)

def check_title(filename):
    """Retrieves the password from the name of the file.

    Args:
        filename (str): name of the file including file extension
    Returns:
        teamname (str): name of the team, which is file name minus the file
                        extension
    """
    if os.path.isfile(filename):
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
        type (str): aborts if file is not 'dir', 'tar', 'zip' or 'lzma',
                    otherwise returns one of these types.
    """
    if os.path.isdir(command_line_argument):
        file_type = "dir"
    elif mimetypes.guess_type(command_line_argument)[1] == 'bzip2':
        file_type = "bz2"
    elif mimetypes.guess_type(command_line_argument)[1] == 'gzip':
        file_type = "gz"
    elif zipfile.is_zipfile(command_line_argument):
        file_type = "zip"
    elif mimetypes.guess_type(command_line_argument)[1] == "xz":
        file_type = "xz"
    else:
        print("Type is unacceptable")
        sys.exit()

    return file_type


def extract(filetype, filename):
    """Determines what type of extraction should be used on the file and calls
       the appropriate extract function. Then returns the directory to be worked
       with.

    Args:
        filetype (str): the type of file. 'dir', 'zip', 'lzma' or 'tar'.
        filename (str): the name of the file as provided from the command line.
                        Will include file extension.
    Returns:
        None
    """
    if filetype == "bz2":
        filelist = extract_tar(filename, filetype)
    elif filetype == "gz":
        filelist = extract_tar(filename, filetype)
    elif filetype == "xz":
        filelist = extract_tar(filename, filetype)
    elif filetype == "zip":
        filelist = extract_zip(filename) 
    else:
        print("it's a directory")

    return filelist

### Extraction Functions ###


def extract_tar(filenametar, comptype):
    """Opens, extracts, and closes tar file.

    Args:
        filenametar (str): the name of the file as provided on the command 
                           line.
    Returns:
        extar (list): the members as a list of TarInfo objects.
    """
    try:
        L = []
        with tarfile.open(filenametar, 'r:{}'.format(comptype)) as tar: 
            for n in tar.getnames():
                L.append(tar.extractfile(n))
        return L
    except tarfile.TarError:
        print("Couldn't open tarfile")


def extract_zip(zipfilename):
    """Opens, extracts, and closes zip files.

    Args:
        zipfile (str): the name of the file as provided on the command line.
    Returns:
        None
   """
    try:
        L = []
        with zipfile.ZipFile(zipfilename) as myzip:
            for n in myzip.namelist():
                L.append(myzip.open(n))
        return L
    except zipfile.BadZipFile:
       print("Couldn't extract zip file")

if __name__ == '__main__':
    main(sys.argv)
