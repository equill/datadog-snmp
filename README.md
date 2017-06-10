Datadog-SNMP
============

A standalone script to poll SNMP targets and forward the results to Datadog, with appropriate tags added and counters converted to rates.
Uses multiprocessing to parallelise things, to get past the scalability limit of datadog-agent's single-threaded nature, and to avoid the Global Interpreter Lock that would otherwise prevent concurrency.

Written for python 3.5, with no attempt at backward compatibility.
