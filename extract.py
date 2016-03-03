# ***REMOVED*** | ***REMOVED***@wwu.edu | 25 February 2016
#
#    The purpose of this program is to determine the file type of a given
# directory or archive and then extract the archive. It will also pull
# out the team name from the title of the directory/archive. 

import os
import sys
import tarfile
import os.path
import lzma
import zipfile

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
    if file_type == "tar":
        extract_tar(argv[1])
    elif file_type == "zip":
        print("will zip later")
        #extract_zip(argv[1])
    elif file_type == "lzma":
        extract_lzma(argv[1])
    else:
        print("it's a directory")


# The function check_title returns the team name from whatever the file name is.
def check_title(filename):
    teamname = os.path.splitext(filename)[0] 
    return teamname

# The function inspect_file determines what type of file is given and returns it 
# as a string.
def inspect_file(command_line_argument):
    
    # Determine the file type.
    if os.path.isdir(command_line_argument):
        type = "dir"
    elif tarfile.is_tarfile(command_line_argument):
        type = "tar"
    elif zipfile.is_zipfile(command_line_argument):
        type = "zip"
    else:
        type = "lzma"

    return type 


# The function extract_tar opens, extracts, and closes a tar file.
def extract_tar(filenametar):
    try:
        tar = tarfile.open(filenametar)
        tar.extractall()
        tar.close()
    except tarfile.TarError:
        print("Couldn't open tarfile")


# The function extract_lzma extracts lzma-compressed files
def extract_lzma(lzfile):
    try:
        lz = lzma.open(lzfile)
        lzma.decompress(lz)
        tar.close()
    except tarfile.TarError:
        print("Couldn't open lzma compressed file with tar")









main(sys.argv)
