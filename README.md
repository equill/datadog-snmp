Datadog-SNMP
============

A standalone script to poll SNMPv2 targets and forward the results to Datadog, with appropriate tags added and counters converted to rates.

Uses multiprocessing to parallelise things, to get past the scalability limit of datadog-agent's single-threaded nature, and to avoid the Global Interpreter Lock that would otherwise prevent concurrency.

Written for python 3.5, with no attempt at backward compatibility.

# Configuration

A JSON-formatted text file is expected; I know comments aren't valid in JSON, but they seemed like the best way of illustrating this:

```
[   // A list of targets in the form of dicts
  {
    "hostname": "localhost",    // Without this, you're not getting far
    "community": "public',      // SNMPv2 community string for authentication
    "metrics": [    // a list of metrics, again as dicts
      {
        // Mandatory attributes
        "oid": "sysUpTime",     // Can be either a name or a numeric OID
        "mib": "SNMPv2-MIB",    // If this isn't specified, it's assumed to be numeric
        // Optional attributes
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
```

See `config.json` for an example.
