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

    # Check for correct number of args and get the file name/path.
    if (len(sys.argv) == 2):
        try:
            if os.path.isfile(argv[1]) or os.pathisdir(argv[1]):
                file_name = argv[1]
        except ValueError:
            print("Error with file.")
    else:
        print("Incorrect number of arguments")
        sys.exit()

    # Determine and return the file type.
    file_type = inspect_file(file_name)

    # Extract based on file type
    extract(file_type, file_name)








## INSPECT_FILE ##
def inspect_file(command_line_argument):
    """Determines which type of file is given.

    Args:
        command_line_argument (str): the name of the file given on the command
                                     line.
    Returns:
        file_type (str): aborts if file is not a directory, gzip, zip or xz compressed file.
                         otherwise returns a string representing one of the four types.
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
        filelist (list): a list containing extracted file objects from the directory.
    """

    if filetype == "bz2" or filetype == "gz" or filetype == "xz":
        extract_tar(filename, filetype)
    elif filetype == "zip":
        extract_zip(filename)
    elif filetype == "dir":
        print("Eventually deal with dir")
    else:
        print("error with file type in extract()")
        sys.exit()







## EXTRACT_TAR ##
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
        sys.exit()


## DECODE ##
def decode(json_file_object):
    """Decodes and extracts contents of the metadata.json file.

    Args:
        json_file_object (???): the extracted metadata.json file object.
    Returns:
        None
    """

    jstr = bytes.decode(json_file_object.read())
    json_data_in_dictionary = json.loads(jstr)





















def extract_zip(zipfilename):
    """Opens, extracts, and closes zip files.

    Args:
        zipfilename (str): the name of the file as provided on the command line.
    Returns:
        L (list): the members of the archive extracted as file objects.
   """
    try:
        with zipfile.ZipFile(zipfilename) as myzip:
            for n in myzip.namelist():
                if os.path.basename(n) == "metadata.json":
                    decode(myzip.extract(n))
                elif os.path.basename(n).endswith('.pub'):
                    print(".pub")
                else:
                    print("other")
    except zipfile.BadZipFile:
       print("Couldn't extract zip file")

if __name__ == '__main__':
    main(sys.argv)
