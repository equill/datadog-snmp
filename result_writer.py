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


# Built-in libraries
import time


# Config variables
#
# The largest number of items to send to Datadog in a single batch
MAX_ITEMS=10
#
# How many seconds to pause when the queue is empty
PAUSE=1

def run(queue, logger):
    '''
    Take whatever's in the queue, and forward it to Datadog.
    '''
    logger.info('Starting writer process')
    while True:
        # If there's nothing in the queue, give it a moment
        if queue.empty():
            logger.debug('Results queue is empty. Sleeping...')
            time.sleep(PAUSE)
        # There's something on the queue; get to work
        else:
            ctr=0   # Counter for limiting the items retrieved
            acc=[]  # Accumulator for results from the queue
            # Retrieve up to MAX_ITEMS results from the queue
            while ctr < MAX_ITEMS:
                if queue.empty():
                    break
                else:
                    acc.append(queue.get())
            # Process the items we accumulated
            logger.info('%d results retrieved: %s' % (len(acc), acc))
            # Clear the accumulator for the next run
            acc[:]=[]
