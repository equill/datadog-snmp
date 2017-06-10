Datadog-SNMP
============

A standalone script to poll SNMPv2 targets and forward the results to Datadog, with appropriate tags added and counters converted to rates.

Uses multiprocessing to parallelise things, to get past the scalability limit of datadog-agent's single-threaded nature, and to avoid the Global Interpreter Lock that would otherwise prevent concurrency.

Written for python 3.5, with no attempt at backward compatibility.

# Configuration

A JSON-formatted text file is expected; note that the parser chokes on any comments in th e file.

```
[   // A list of targets in the form of dicts
  {
    "hostname": "localhost",    // Without this, you're not getting far
    "community": "public',      // SNMPv2 community string for authentication
    "metrics": [    // a list of metrics, again as dicts
      {
        // Mandatory attributes
        "oid": "sysName",       // Can be either a name or a numeric OID
        "mib": "SNMPv2-MIB",    // If this isn't specified, it's assumed to be numeric
        // Optional attributes
        "tags": ["hostname:localhost"], // Tags to forward to Datadog with this metric
        "metricname": "hostname"        // The name to give Datadog.
                                        // If unspecified, the OID will be used.
      }
    ]
  }
]
```

See `config.json` for an example.
