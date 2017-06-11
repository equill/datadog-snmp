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
import result_writer
import snmp_query


# Settings

# Where to expect the config file,
# if it's not specified via --config
DEFAULT_CONFIGPATH='config.json'

# How many seconds to pause between runs
PERIOD_DEFAULT=60


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
    logger.debug('Attempting to read config file "%s"' % filepath)
    infile=open(filepath, 'r')
    configs=json.load(infile)
    infile.close()
    logger.info('Parsed config file %s' % filepath)
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
    queue=mp.Queue()    # For passing results from SNMP queries to the Datadog writer
    # Read the initial config file, and remember when we read it
    configs=read_configs(configpath)
    config_mtime=int(os.path.getmtime(configpath))
    if 'period' in configs['global']:
        period=configs['global']['period']
    else:
        period=PERIOD_GLOBAL
    # Start the process that reads the queue and feeds Datadog
    writer=mp.Process(target=result_writer.run, args=(queue, configs['global']['datadog_api_key'], logger), name='writer')
    writer.start()
    # Periodically poll the targets
    while True:
        starttime=int(time.time())
        logger.info('Starting run with timestamp %d' % starttime)
        # Check whether to re-read the configs
        config_curr_mtime=int(os.path.getmtime(configpath))
        logger.debug('Config file last-modified timestamp: %d' % config_curr_mtime)
        if config_curr_mtime > config_mtime:
            logger.info("Config file's timestamp has changed from %s to %s; re-reading." % (config_mtime, config_curr_mtime))
            configs=read_configs(configpath)
            config_mtime=int(os.path.getmtime(configpath))
        # Kick off the SNMP-querying processes
        for target in configs['metrics']:
            proc=mp.Process(target=snmp_query.query_device,
                    args=(target, logger, state, period, queue),
                    name=target['hostname'])
            procs.append(proc) # Add the process to the list before starting it
            proc.start()
        # Gather the processes back in
        for proc in procs:
            proc.join()
        # Prove we got something in the state dict
        logger.debug('State: %s' % state)
        # Pause until the next run
        # being reasonably sure to start _on_ the minute (or whatever)
        endtime=int(time.time())
        delay=((endtime + period) % period)
        if delay == 0:
            delay == period
        logger.info('Run complete at timestamp %d after %d seconds. Pausing %d seconds for the next run.' % (endtime, endtime - starttime, delay))
        time.sleep(delay)
    # Reclaim the writer
    writer.terminate()
    writer.join()
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
    logger.info('Logging is ready. Starting main program.')
    main(logger, configpath)
