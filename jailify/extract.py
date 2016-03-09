# ***REMOVED*** | ***REMOVED***@wwu.edu | 04 March 2016
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
    directory = extract(file_type, file_name)


def check_title(filename):
    """Retrieves the password from the name of the file.

    Args:
        filename (str): name of the file including file extension
    Returns:
        teamname (str): name of the team, which is file name minus the file
                        extension
    """
    teamname = os.path.splitext(filename)[0]
    return teamname


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
    elif tarfile.is_tarfile(command_line_argument):
        file_type = "tar"
    elif zipfile.is_zipfile(command_line_argument):
        file_type = "zip"
    elif mimetypes.guess_type(command_line_argument) == "lzma":
        file_type = "lzma"
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
        extractedfile (dir): the extracted file.
    """
    if filetype == "tar":
        extractedfile = extract_tar(filename)
        extractedfile.close()
    elif filetype == "zip":
        extractedfile = extract_zip(filename)
        extractedfile.close()
    elif filetype == "lzma":
        extractedfile = extract_lzma(filename) 
        extractedfile.close()
    else:
        extractedfile = filename
        print("it's a directory")
    return extractedfile

### Extraction Functions ###


def extract_tar(filenametar):
    """Opens, extracts, and closes tar file.

    Args:
        filenametar (str): the name of the file as provided on the command 
                           line.
    Returns:
        tar (dir): extracted tar file
    """
    try:
        tar = tarfile.open(filenametar)
        tar.extractall()
        return tar
    except tarfile.TarError:
        print("Couldn't open tarfile")


def extract_lzma(lzfile):
    """Extracts lzma compressed files.

    Args:
        lzfile (str): the name of the file as provided on the command line.
    Returns:
        lz (file):extracted lzma directory. Must be closed after returning.
    """
    try:
        lz = tarfile.open(lzfile, 'r:xz')
        lz.extractall()
        return lz
    except  tarfile.TarError:
        print("LZMA extraction error")



def extract_zip(zipfilename):
    """Opens, extracts, and closes zip files.

    Args:
        zipfile (str): the name of the file as provided on the command line.
    Returns:
        myzip (dir): the extracted zip file.
   """
    try:
        myzip = zipfile.ZipFile(zipfilename)
        myzip.extractall()
        return myzip
    except zipfile.BadZipFile:
       print("Couldn't extract zip file")

if __name__ == '__main__':
    main(sys.argv)
