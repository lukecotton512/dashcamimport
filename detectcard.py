#!/usr/bin/python3

# detectcard.py
# Luke Cotton
# A script for detecting our SD card being mounted.

import sys
import signal
import logging
import configparser

# Our logger.
LOGGER = logging.getLogger(__name__)

def main():
    # Get path to import directory and exit if we don't have it.
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <configfile>")
        exit(1)

    # Read everything from the config file.
    configName = sys.argv[1]

    configfile = configparser.ConfigParser()
    configfile.read(configName)

    config = configfile['detectcard']

    cardName = config['sdcardname']
    importDir = config['importdir']
    subPath = config['sdcardsubpath']
    mountPath = config['sdcardmountpath']
    logFilePath = config['logfilepath']

    # Setup logging.
    logging.basicConfig(encoding='utf-8', level=logging.DEBUG, handlers=[
        logging.FileHandler(logFilePath),
        logging.StreamHandler()
    ])

    # Setup response to signals.
    signal.signal(signal.SIGHUP, handleSignal)
    signal.signal(signal.SIGTERM, handleSignal)
    signal.signal(signal.SIGINT, handleSignal)

    if sys.platform.startswith("linux"):
        # We are on linux
        import detectcardlinux
        LOGGER.info("[linux] Starting detection script.")
        detectcardlinux.do_detect(cardName, mountPath, importDir, subPath)
    elif sys.platform.startswith("darwin"):
        import detectcardmacos
        LOGGER.info("[macos] Starting detection script.")
        detectcardmacos.do_detect(cardName, mountPath, importDir, subPath)


# Handle a signal.
def handleSignal(sig, frame):
    LOGGER.warning("Signal received")
    exit()

if __name__ == "__main__":
    main()