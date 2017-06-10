#!/usr/bin/env python

# Query remote devices via SNMP
# and update the shared storage dict.
#
# Note that we're not on python3.6 yet,
# so shared substructures don't work.
# This is why the indices are crappy-looking composite strings.


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

# FIXME: only needed until we get SNMP queries working.
# datetime is purely to produce visibly changing output.
import time


def query_device(details, logger, state):
    '''
    When completed, will send an SNMP query to a device, and report on the results.
    '''
    hostname=details['hostname']
    # Process the metrics in turn
    for metric in details['metrics']:
        # Generate the index in the shared-state dict
        index='%s-%s' % (hostname, metric)
        # Dummy result, used in place of actual SNMP results
        result=time.time()
        # If this is the first run, the index won't already be in the dict
        if index in state:
            # To simulate changes in SNMP counters, calculate the difference between
            # the current value and the stored one
            diff = result - state[index]
            logger.info('%s delta = %s' % (index, diff))
        # This is the first run; log it so the operator knows what's going on.
        else:
            logger.info('First run for %s; skipping the diff on this run' % index)
        # Set the result
        logger.info('Adding %s:%s to the state dict' % (metric, result))
        state[index]=result
    return True
