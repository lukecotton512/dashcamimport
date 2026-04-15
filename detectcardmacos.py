#!/usr/bin/python3

# detectcardmacos.py
# Luke Cotton
# macOS version of a script for detecting our SD card being mounted.

import objc
import CoreFoundation
import DiskArbitration
import logging
from Foundation import NSObject

import dashcamimport

_ptrs = {}

# Our logger.
LOGGER = logging.getLogger(__name__)

# Start up detection.
def do_detect(cardName, mountPath, importDir, subPath):
    session = DiskArbitration.DASessionCreate(None)

    context = {
        "importDir": importDir,
        "subPath": subPath
    }

    context_id = id(context)

    _ptrs[context_id] = context

    DiskArbitration.DARegisterDiskDescriptionChangedCallback(
        session,
        {
            DiskArbitration.kDADiskDescriptionMediaRemovableKey: 1,
            DiskArbitration.kDADiskDescriptionVolumeNameKey: cardName
        },
        [DiskArbitration.kDADiskDescriptionVolumePathKey],
        did_detect,
        context_id
    )

    DiskArbitration.DASessionScheduleWithRunLoop(
        session,
        CoreFoundation.CFRunLoopGetCurrent(),
        CoreFoundation.kCFRunLoopDefaultMode
    )

    LOGGER.info("[macos] Listening for SD card.")
    CoreFoundation.CFRunLoopRun()

# Handler to detect our disk
@objc.callbackFor(DiskArbitration.DARegisterDiskDescriptionChangedCallback)
def did_detect(disk, keys, id):
    context = _ptrs[id]
    bsdName = DiskArbitration.DADiskGetBSDName(disk).decode('utf-8')
    diskDict = DiskArbitration.DADiskCopyDescription(disk)
    mountPathURL = diskDict.get(DiskArbitration.kDADiskDescriptionVolumePathKey)
    if mountPathURL is not None:
        mountPath = mountPathURL.path()
        LOGGER.info(f"[macos] Disk detected: {bsdName} {mountPath}")

        importDir = context["importDir"]
        subPath = context["subPath"]
        dashcamimport.doImport(mountPath, importDir, subPath)
    
