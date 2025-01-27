# CPU Monitor

A Python script to monitor CPU usage, using the locust-coding-challenge API.

## Installation

Run the Makefile task:

```bash
make install
```

## Execute

Execute the program with:

```
cpu_monitor --username demo --password demo123
```

See all the options with `cpu_monitor -h`:

```
CPU Usage Monitoring Script

options:
  -h, --help            show this help message and exit
  --api-url API_URL     Base API URL (default: http://localhost:8888)
  --username USERNAME   Username for API authentication
  --password PASSWORD   Password for API authentication
  --name NAME           Name of test the run.
  --interval INTERVAL   Interval in seconds between CPU usage measurements (default: 5.0)
  --threshold THRESHOLD
                        CPU usage threshold percentage for notifications (default: 75.0)
```
