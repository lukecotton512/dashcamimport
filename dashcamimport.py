#!/usr/bin/python3

# dashcamimport.py
# Luke Cotton
# A script for importing dashcam footage from a SD card.

# Imports.
import pyudev
import signal
import os
from pathlib import Path

# Constants.
SD_CARD_NAME = "NEXTBASE"
SD_CARD_MOUNT_PATH = "/mnt/sdcardmnt"

# Entry point for script.
def main():
    # Setup response to signals.
    signal.signal(signal.SIGHUP, handleSignal)
    signal.signal(signal.SIGTERM, handleSignal)

    # Setup monitor to watch for dashcam SD card being mounted.
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block', device_type='partition')

    # Monitor for the SD card.
    for device in iter(monitor.poll, None):
        if device.action == 'add':
            devicelabel = device.get('ID_FS_LABEL', 'unknown')
            print("{0}: {1}".format(device.device_node, devicelabel))
            if devicelabel == SD_CARD_NAME:
                mountSDCard(device.device_node)

# Mount our SD card.
def mountSDCard(devnode):
    print("Mounting SD Card: {0}".format(devnode))
    
    # Check to see if mount point exists.
    mountPath = Path(SD_CARD_MOUNT_PATH)
    if mountPath.exists():
        # Check to see if we are not already mounted.
        if mountPath.is_mount():
            # We are already mounted, so get out of here
            return
    else:
        # Create the mount point.
        os.mkdir(SD_CARD_MOUNT_PATH)
    
    # Mount the SD card.
    os.system("mount {0} {1}".format(devnode, SD_CARD_MOUNT_PATH))

    
# Handle a signal.
def handleSignal():
    print("Signal received")
    exit()

# Call main if loaded from command line.
if __name__ == "__main__":
    main()