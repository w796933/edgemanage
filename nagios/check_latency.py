#!/usr/bin/env python

import sys
import time
import json
import argparse
import glob
import os.path

DEFAULT_CRIT=2.0
DEFAULT_WARN=4.0
# Window to check for a fetch, in seconds
TIME_WINDOW=60

OUTPUT_LABEL="ACTIVE_EDGE_LATENCY"
STATUS_MAP = {0: "OK",
              1: "WARN",
              2: "CRIT",
              3: "UKNOWN"}

class CheckLatency(object):

    def __init__(self, edgehealth_dir):
        self.latency_map = {}
        self.now = time.time()

        for health_file in glob.glob("%s/*edgestore" % edgehealth_dir):
            with open(health_file) as health_f:
                edge_name = os.path.basename(health_file).partition(".edgestore")[0]
                health_json = json.loads(health_f.read())
                if "fetch_times" not in health_json or not health_json["fetch_times"]:
                    # Skip uninitialised edges, or edges that have no data
                    continue

                latest_fetch_time = sorted(health_json["fetch_times"].keys())[-1]
                if float(latest_fetch_time) < (self.now - TIME_WINDOW):
                    # Skip fetches that are too old
                    print "Skipping %s as fetch time was %f ago" % (edge_name,
                                                                    self.now - latest_fetch_time)
                    continue
                self.latency_map[edge_name] = health_json["fetch_times"][latest_fetch_time]

    def check_rotation(self, warn, crit):
        worst_latency = None
        nagios_status = 0
        edge_name = None
        nagios_message = "No edges over threshold latencies"
        for edge_name, fetch_value in self.latency_map.iteritems():
            if not worst_latency or fetch_value > worst_latency:
                worst_latency = fetch_value
                edge_name = edge_name
        if not worst_latency:
            nagios_message = "No fetch data!"
            nagios_status = 3
        elif worst_latency >= crit:
            nagios_status = 2
            nagios_message = "Slowest active edge %s responded in %f" % (edge_name, worst_latency)
        elif worst_latency >= warn:
            nagios_status = 1
            nagios_message = "Slowest active edge %s responded in %f" % (edge_name, worst_latency)

        return (nagios_status, "%s %s %s | time=%f edge=%s" % (OUTPUT_LABEL,
                                                               STATUS_MAP[nagios_status],
                                                               nagios_message, worst_latency,
                                                               edge_name))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Nagios check for Edgemanage fetch latency.')
    parser.add_argument("edgehealth", nargs=1, action="store",
                        help="Path to the edgemanage edge health store")
    parser.add_argument("--warn", "-w", action="store", dest="warn",
                        help="Path to the edgemanage state file",
                        default=DEFAULT_WARN, type=int)
    parser.add_argument("--critical", "-c", action="store", dest="crit",
                        help="Path to the edgemanage state file",
                        default=DEFAULT_CRIT, type=int)
    args = parser.parse_args()
    c = CheckLatency(args.edgehealth[0])
    status, message = c.check_rotation(args.warn, args.crit)
    print message
    sys.exit(status)
