#!/usr/bin/python3

# detectcard.py
# Luke Cotton
# A script for detecting our SD card being mounted.

# Imports.
import pyudev
import signal
import os
import sys
import logging
from pathlib import Path

import dashcamimport

# Constants.
SD_CARD_NAME = "NEXTBASE"
SD_CARD_MOUNT_PATH = "/mnt/dashcam"
SD_CARD_SUB_PATH = "DCIM/PROTECTED"
LOG_FILE_PATH = "detectcard.log"

# Entry point for script.
def main():
    # Setup logging.
    logging.basicConfig(filename=LOG_FILE_PATH, encoding='utf-8', level=logging.DEBUG)

    # Get path to import directory and exit if we don't have it.
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <import directory>")
        exit(1)
    
    importDir = sys.argv[1]

    # Setup response to signals.
    signal.signal(signal.SIGHUP, handleSignal)
    signal.signal(signal.SIGTERM, handleSignal)
    signal.signal(signal.SIGINT, handleSignal)

    # Setup monitor to watch for dashcam SD card being mounted.
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block', device_type='partition')

    # Monitor for the SD card.
    for device in iter(monitor.poll, None):
        if device.action == 'add':
            devicelabel = device.get('ID_FS_LABEL', 'unknown')
            devicefstype = device.get('ID_FS_TYPE', '')
            logging.info(f"{device.device_node}: {devicelabel}")
            if devicelabel == SD_CARD_NAME:
                mountStatus = mountSDCard(device.device_node, SD_CARD_MOUNT_PATH, devicefstype)
                if mountStatus == 0:
                    dashcamimport.doImport(SD_CARD_MOUNT_PATH, importDir, SD_CARD_SUB_PATH)
                    unmountSDCard(SD_CARD_MOUNT_PATH)
                else:
                    exit()

# Mount our SD card.
def mountSDCard(devnode, mountPoint, fstype=''):
    logging.info(f"Mounting SD Card: {devnode}")
    
    # Check to see if mount point exists.
    mountPath = Path(mountPoint)
    if mountPath.exists():
        # Check to see if we are not already mounted.
        if mountPath.is_mount():
            # We are already mounted, so get out of here
            return
    else:
        # Create the mount point.
        os.mkdir(mountPoint)
    
    # Mount the SD card.
    typearg = ""
    if fstype != "":
        typearg = f" -t {fstype}"

    status = os.system(f"mount{typearg} {devnode} {mountPoint}")

    if status == 0:
        logging.info(f"Mounted {devnode} at {mountPoint}")
    else:
        logging.error(f"Failed to mount {devnode} at {mountPoint}")

    return status

# Unmount our SD card.
def unmountSDCard(mountPath):
    # Check to see if the card is mounted
    mountPath = Path(mountPath)
    if mountPath.exists() and mountPath.is_mount():
        # Unmount the card.
        status = os.system(f"umount {mountPath}")

        # Check to make sure we were successful or not and print a corresponding message.
        if status == 0:
            logging.info(f"Unmounted SD card {mountPath} successfully.")
        else:
            logging.error(f"Failed to unmount SD card {mountPath}.")

    
# Handle a signal.
def handleSignal(sig, frame):
    print("Signal received")
    exit()

# Call main if loaded from command line.
if __name__ == "__main__":
    main()