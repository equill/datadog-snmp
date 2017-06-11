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


# Third-party modules
import pysnmp.hlapi
import re

# Utility functions

def snmpGet(hostname, oid, community, logger, mib=False, port=161):
    '''
    Perform an SNMP GET for a single OID or scalar attribute.
    Return only the value.
    '''
    # Handle the case of an unspecified MIB
    if mib:
        cmd=pysnmp.hlapi.getCmd(
                # Create the SNMP engine
                pysnmp.hlapi.SnmpEngine(),
                # Authentication: set the SNMP version (2c) and community-string
                pysnmp.hlapi.CommunityData(community, mpModel=1),
                # Set the transport and target: UDP, hostname:port
                pysnmp.hlapi.UdpTransportTarget((hostname, port)),
                # Context is a v3 thing, but appears to be required anyway
                pysnmp.hlapi.ContextData(),
                # Specify the MIB object to read.
                # The 0 means we're retrieving a scalar value,
                # And we're helpfully .
                pysnmp.hlapi.ObjectType(pysnmp.hlapi.ObjectIdentity(mib, oid, 0)))
    else:
        cmd=pysnmp.hlapi.getCmd(
                # Create the SNMP engine
                pysnmp.hlapi.SnmpEngine(),
                # Authentication: set the SNMP version (2c) and community-string
                pysnmp.hlapi.CommunityData(community, mpModel=1),
                # Set the transport and target: UDP, hostname:port
                pysnmp.hlapi.UdpTransportTarget((hostname, port)),
                # Context is a v3 thing, but appears to be required anyway
                pysnmp.hlapi.ContextData(),
                # Specify the object to read.
                # The 0 means we're retrieving a scalar value.
                pysnmp.hlapi.ObjectType(pysnmp.hlapi.ObjectIdentity(oid))
                )
    # Use pysnmp to retrieve the data
    errorIndication, errorStatus, errorIndex, varBinds = next(cmd)
    # Handle the responses
    if errorIndication:
        logger.error(errorIndication)
        return False
    elif errorStatus:
        logger.error('%s at %s' % (errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        return False
    # If we actually got something, return it in human-readable form
    else:
        return varBinds[0][1].prettyPrint()


def query_device(details, logger, state):
    '''
    Send an SNMP query to a device, and report on the results.
    '''
    hostname=details['hostname']
    logger.info('Querying host %s' % hostname)
    # Process the metrics in turn
    for metric in details['metrics']:
        # Shorter references
        oid=metric['oid']
        metricname=metric['metricname']
        # Properly handle an unspecified MIB
        if 'mib' in metric:
            mib=metric['mib']
        else:
            mib=False
        # Generate the index in the shared-state dict
        index='%s-%s' % (hostname, oid)
        # Fetch the result
        if mib:
            logger.debug('Fetching OID %s::%s from target %s' % (mib, oid, hostname))
        else:
            logger.debug('Fetching OID %s from target %s' % (oid, hostname))
        # Actually fetch the result amid all the mad logging
        val=int(snmpGet(hostname, oid, details['community'], logger, mib))
        # Do some more mad logging
        if mib:
            logger.debug('%s - %s::%s (%s) = %s' % (hostname, mib, oid, metricname, val))
        else:
            logger.debug('%s - %s (%s) = %s' % (hostname, oid, metricname, val))
        #
        # Handling counter-type metrics
        if 'counter' in metric:
            # If this is the first run, the index won't already be in the dict
            if index in state:
                # To simulate changes in SNMP counters, calculate the difference between
                # the current value and the stored one
                diff = val - state[index]
                logger.debug('%s delta = %s' % (index, diff))
            # This is the first run; log it so the operator knows what's going on.
            else:
                logger.debug('First run for %s; skipping the diff on this run' % index)
            # Set the result
            logger.debug('Adding %s:%s to the state dict' % (metric, val))
            state[index]=val
    return True
