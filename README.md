Datadog-SNMP
============

**Obsolete**
The built-in SNMP integration in Datadog-agent now works well enough that this is not required, so I've abandoned further work.

A standalone script to poll SNMPv2 targets and forward the results to Datadog, with appropriate tags added and counters converted to rates.

Uses multiprocessing to parallelise things, to get past the scalability limit of datadog-agent's single-threaded nature, and to avoid the Global Interpreter Lock that would otherwise prevent concurrency.

Automatically re-reads the config file if it's been changed. Does this by checking the last-modified time at the start of each run, and comparing that to the value stored last time it was read.

Written for python 3.5, with no attempt at backward compatibility.

## Limitations
- only handles scalars. Tables are not handled.
- tags are per-metric; there's no way of specifying global or per-target tags
    - this _may_ be added in future; it simply hasn't been implemented so far.

# Configuration

A JSON-formatted text file is expected; I know comments aren't valid in JSON, but they seemed like the best way of illustrating this:

```
{
    "global": {
        "datadog_api_key": "key goes here",
        "period": 60    // Optional; default is 60 seconds
    },
    "metrics": [   // A list of targets in the form of dicts
    {
        "hostname": "localhost",    // Without this, you're not getting far
        "address": "127.0.0.1"      // Optional; if the hostname resolves correctly, you don't need this
        "community": "public',      // SNMPv2 community string for authentication
            "metrics": [    // a list of metrics, again as dicts
            {
                // Mandatory attributes
                "oid": "sysUpTime",     // Can be either a name or a numeric OID
                // Optional attributes
                "mib": "SNMPv2-MIB",    // If this isn't specified, the OID is used unqualified.
                "tags": ["hostname:localhost"], // Tags to forward to Datadog with this metric
                "metricname": "hostname",       // The name to give Datadog;
                // if unspecified, the OID will be used.
                "counter": "true"       // If set, prompts the script to autoconvert it
                    // to a rate before sending to Datadog.
                    // The actual value doesn't matter
            }
            ]
    }
    ]
}
```

If a MIB is specified, the OID will be checked for a trailing index, e.g. `ifInOctets.1`. If there is one, it will be used; if not, 0 will be assumed, which is the SNMP default for a single-value OID.

See `config.json` for an example.
