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
import sys
import time

# Local modules
import snmp_query


# The actual code

def read_configs(filepath="config.json"):
    '''
    When complete, will read a config file and return the result.
    '''
    with open(filepath) as infile:
        configs=json.load(infile)
    return configs

def main(logger):
    '''
    Demo function to test multiprocessing
    '''
    # Process-management
    procs=[]            # A list of running processes
    mgr=mp.Manager()    # Source of shared-state structures
    state=mgr.dict()    # The shared dict we'll use for sharing state
    while True:
        # Kick off the processes
        for details in read_configs():
            proc=mp.Process(target=snmp_query.query_device,
                    args=(details, logger, state),
                    name=details['hostname'])
            procs.append(proc) # Add the process to the list before starting it
            proc.start()
        # Gather the processes back in
        for proc in procs:
            proc.join()
        # Prove we got something in the state dict
        print(state)
        # Pause a second
        time.sleep(10)
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
    args=parser.parse_args()
    # Set debug logging, if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
    # Run the script
    main(logger)
