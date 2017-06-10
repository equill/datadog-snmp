#!/usr/bin/env python

# Control script
#
# All the actual action happens via imported local modules.
# This just does the management overhead, like reading configs,
# setting up logging and handling the multiprocessing stuff.


#   Copyright [2017] [James Fleming <james@electronic-quill.net]
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


# Included batteries
import argparse
import json
import logging
import multiprocessing as mp
import os
import sys
import time

# Local modules
import snmp_query


# Settings

# Where to expect the config file,
# if it's not specified via --config
DEFAULT_CONFIGPATH='config.json'

# How many seconds to pause between runs
PERIOD=10


# The actual code

def read_configs(configpath):
    '''
    Read a config file and return the result.
    '''
    # Figure out where to look for the config file
    if configpath:
        filepath=configpath
    else:
        filepath=DEFAULT_CONFIGPATH
    # Open the file and read it
    logger.debug('Attempting to open config file "%s"' % filepath)
    with open(filepath) as infile:
        configs=json.load(infile)
    return configs

def main(logger, configpath):
    '''
    Make stuff happen
    - read the configs, and automagically re-read them if the file's last-modified
      time changes
    - handle the multiprocessing overhead
    '''
    # Process-management
    procs=[]            # A list of running processes
    mgr=mp.Manager()    # Source of shared-state structures
    state=mgr.dict()    # The shared dict we'll use for sharing state
    # Read the initial config file, and remember when we read it
    configs=read_configs(configpath)
    config_mtime=os.path.getmtime(configpath)
    while True:
        # Check whether to re-read the configs
        if os.path.getmtime(configpath) != config_mtime:
            logger.debug('Config file has changed; re-reading.')
            config_mtime=os.path.getmtime(configpath)
            configs=read_configs(configpath)
        # Kick off the processes
        for details in configs:
            proc=mp.Process(target=snmp_query.query_device,
                    args=(details, logger, state),
                    name=details['hostname'])
            procs.append(proc) # Add the process to the list before starting it
            proc.start()
        # Gather the processes back in
        for proc in procs:
            proc.join()
        # Prove we got something in the state dict
        logger.debug('State: %s' % state)
        # Pause a second
        time.sleep(PERIOD)
    # Explicitly return _something_
    return True


# When invoked as a script, rather than a library

if __name__ == '__main__':
    # Set up logging to STDERR
    mp.log_to_stderr()
    logger=mp.get_logger()
    logger.setLevel(logging.INFO)   # Required because the default is NOTSET
    # Get the command-line arguments
    parser = argparse.ArgumentParser(description='Perform SNMP discovery on a host, returning its data in a single structure.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--config', action='store', help='Path to the config file')
    args=parser.parse_args()
    # Set debug logging, if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
    # Check whether the default config path was overridden
    if args.config:
        configpath=args.config
    else:
        configpath=False
    # Run the script
    main(logger, configpath)
