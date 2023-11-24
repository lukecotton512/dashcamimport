#!/usr/bin/python3

# detectcard.py
# Luke Cotton
# A script for detecting our SD card being mounted.

# Imports.
import pyudev
import signal
import subprocess
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
LOGGER = logging.getLogger(__name__)

# Entry point for script.
def main():
    # Setup logging.
    logging.basicConfig(encoding='utf-8', level=logging.DEBUG, handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ])

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
            LOGGER.info(f"{device.device_node}: {devicelabel}")
            if devicelabel == SD_CARD_NAME:
                mountStatus = mountSDCard(device.device_node, SD_CARD_MOUNT_PATH)
                if mountStatus == 0:
                    dashcamimport.doImport(SD_CARD_MOUNT_PATH, importDir, SD_CARD_SUB_PATH)
                    unmountSDCard(SD_CARD_MOUNT_PATH)
                else:
                    exit()

# Mount our SD card.
def mountSDCard(devnode, mountPoint):
    LOGGER.info(f"Mounting SD Card: {devnode}")
    
    # Check to see if mount point exists.
    mountPath = Path(mountPoint)
    if mountPath.exists():
        # Check to see if we are not already mounted.
        if mountPath.is_mount():
            # We are already mounted, so get out of here
            return
    else:
        # Create the mount point.
        mountPath.mkdir()
    
    # Mount command depends on whether or not we are root.
    # If we are not root, then just pass the dev node.
    # Otherwise, pass the mount point.
    # Mount the SD card.
    if os.getuid() == 0:
        status = subprocess.run(["mount", devnode, mountPoint], capture_output=True)
    else:
        status = subprocess.run(["mount", devnode], capture_output=True)

    if status.returncode == 0:
        LOGGER.info(f"Mounted {devnode} at {mountPoint}")
    else:
        err = str(status.stderr, 'utf-8')
        LOGGER.error(err)
        LOGGER.error(f"Failed to mount {devnode} at {mountPoint}")

    return status.returncode

# Unmount our SD card.
def unmountSDCard(mountPath):
    # Check to see if the card is mounted
    mountPath = Path(mountPath)
    if mountPath.exists() and mountPath.is_mount():
        # Unmount the card.
        status = subprocess.run(["umount", mountPath], capture_output=True)

        # Check to make sure we were successful or not and print a corresponding message.
        if status.returncode == 0:
            LOGGER.info(f"Unmounted SD card {mountPath} successfully.")
        else:
            err = str(status.stderr, 'utf-8')
            LOGGER.error(err)
            LOGGER.error(f"Failed to unmount SD card {mountPath}.")

    
# Handle a signal.
def handleSignal(sig, frame):
    LOGGER.warning("Signal received")
    exit()

# Call main if loaded from command line.
if __name__ == "__main__":
    main()