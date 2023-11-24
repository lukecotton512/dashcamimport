#!/usr/bin/python3

# dashcamimport.py
# Luke Cotton
# A script for importing dashcam footage from somewhere (like a SD card).

# Imports.
import sys
import re
import shutil
import logging
from datetime import datetime
from pathlib import Path

# Our logger.
LOGGER = logging.getLogger(__name__)

# Entry point for script.
def main():
    # Setup logging.
    logging.basicConfig(format='%(message)s', encoding='utf-8', level=logging.DEBUG)

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
def doImport(importSrc, importFolder, subpath = ""):
    # Get a list of all files from the SD card.
    LOGGER.info("Starting import from SD card.")
    importPath = Path(importSrc)
    destPath = Path(importFolder)
    if destPath.exists():
        protectedPath = importPath / subpath
        if protectedPath.exists() and protectedPath.is_dir():
            for path in protectedPath.glob('*.[Mm][Pp]4'):
                copyFile(path, destPath)
        else:
            LOGGER.error(f"Import directory '{importSrc}' is invalid!")
    else:
        LOGGER.error(f"Destination directory '{importFolder} does not exist!")

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
        LOGGER.info(f"Processing {file.name} ({foldername}).")
        folderpath = importFolder / foldername
        folderpath.mkdir(exist_ok=True)
        try:
            shutil.copy(str(file), str(folderpath))
        except IOError as ex:
            LOGGER.error(f"Error copying {file.name}: {ex.strerror}")
        else:
            LOGGER.info("Done!")
    else:
        LOGGER.error(f"File {file} does not match the date pattern. Ignoring.")

# Call main if loaded from command line.
if __name__ == "__main__":
    main()