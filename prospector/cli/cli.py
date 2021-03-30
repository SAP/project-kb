#!/usr/bin/python3

import os, sys
import argparse
import configparser
from pathlib import Path
import pprint
import requests
import logging
logger = logging.getLogger('prospector')

# VERSION = '0.1.0'
# SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
# print(SCRIPT_PATH)

def parseArguments():
    parser = argparse.ArgumentParser(description="Prospector CLI")
    parser.add_argument("vulnerability_id", nargs='?', help="ID of the vulnerability to analyze")

    parser.add_argument("-c", "--conf",
                        help="specify configuration file")

    parser.add_argument("-p", "--ping",
                        help="Contact server to check it's alive",
                        action="store_true")  

    parser.add_argument("-f", "--force",
                        help="overwrite outputfile if it exists",
                        action="store_true")

    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity",
                        action="store_true")

    parser.add_argument("-d", "--debug",
                    help="increase output verbosity even more and output stack-traces on exceptions",
                    action="store_true")

    return parser.parse_args()

def getConfiguration(customConfigFile=None):
    # simple is better: only one configuration file is
    # taken into account, no overriding of options from
    # one file to the other!

    # the order is (as soon as one is found, the rest is ignored):
    # 1) the file passed as argument to this function
    # 2) ./prospector.conf
    # 3) ~/.prospector/conf

    localConfigFile = os.path.join(os.getcwd(), 'prospector.conf')
    userConfigFile = os.path.join(Path.home(), '.prospector/conf')
    
    config = configparser.ConfigParser()

    if customConfigFile and os.path.isfile(customConfigFile):
        configFile = customConfigFile
    elif os.path.isfile(localConfigFile):
        configFile = localConfigFile
    elif os.path.isfile(userConfigFile):
        configFile =  userConfigFile
    else:
        return None

    print("Loading configuration from " + configFile)
    config.read(configFile)
    return config
   
def main(): 

    args = parseArguments()
    configuration = getConfiguration(args.conf)

    if configuration is None:
        print("Invalid configuration, exiting.")
        sys.exit(-1)

    verbose = configuration['global'].getboolean('verbose')
    if args.verbose:
        verbose = args.verbose

    debug = configuration['global'].getboolean('debug')
    if args.debug:
        debug = args.debug

    vulnerability_id = args.vulnerability_id

    if debug:
        verbose = True
    
    if verbose:
        print("Using the following configuration:")
        pprint.pprint({section: dict(configuration[section]) for section in configuration.sections()})

    if verbose:
        print("Vulnerability ID: " + vulnerability_id)
    
    if args.ping:
        srv = configuration['global']['server']

        if verbose:
            print("Contacting server " + srv)

        try:
            response = requests.get(srv)
            if response.status_code != 200:
                print("Server replied with an unexpected status.")
            else:
                print("Server ok!")
        except:
            print("Server did not reply")

if __name__ == "__main__": # pragma: no cover   
    main()
