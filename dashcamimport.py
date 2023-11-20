#!/usr/bin/python3

# dashcamimport.py
# Luke Cotton
# A script for importing dashcam footage from a SD card.

# Imports.
import sys
import re
import shutil
from datetime import datetime
from pathlib import Path

# Constants.
SD_CARD_NAME = "NEXTBASE"
SD_CARD_MOUNT_PATH = "/mnt/sdcardmnt"

# Entry point for script.
def main():
    # Check arguments.
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <sdcard> <importfolder>")
        return
    
    # Our arguments.
    sdcard = sys.argv[1]
    importFolder = sys.argv[2]

    # Do SD card copy.
    doImport(sdcard, importFolder)

# Import footage from SD card.
def doImport(importSrc, importFolder):
    # Get a list of all files from the SD card.
    print("Starting import from SD card.")
    importPath = Path(importSrc)
    destPath = Path(importFolder)
    if destPath.exists():
        protectedPath = importPath / 'DCIM' / 'PROTECTED'
        if protectedPath.exists() and protectedPath.is_dir():
            for path in protectedPath.glob('*.[Mm][Pp]4'):
                copyFile(path, destPath)
        else:
            print(f"Import directory '{importSrc}' is invalid!")
    else:
        print(f"Destination directory '{importFolder} does not exist!")

# For an item, copy it into the import folder,
# Creating a datestamped folder.
def copyFile(file: Path, importFolder: Path):
    # Parse the date of the file name.
    filename = file.name
    match = re.search(r"\d{6}_\d{6}", filename)
    datestr = match.group()
    if datestr is not None:
        # Parse date to get folder
        timestamp = datetime.strptime(datestr, "%y%m%d_%H%M%S")
        foldername = timestamp.strftime("%Y-%m-%d")
        print(f"Processing {file.name} ({foldername}).")
        folderpath = importFolder / foldername
        folderpath.mkdir(exist_ok=True)
        try:
            shutil.copy(str(file), str(folderpath))
        except IOError as ex:
            print(f"Error copying {file.name}: {ex.strerror}")
        else:
            print("Done!")
    else:
        print(f"File {file} does not match the date pattern. Ignoring.")

# Call main if loaded from command line.
if __name__ == "__main__":
    main()