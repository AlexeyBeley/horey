"""
Common data for tests
"""
import os
import json

ses_events_dir = os.path.join(os.path.dirname(__file__), "ses_messages")
ses_events = []
for file_name in os.listdir(ses_events_dir):
    with open(os.path.join(ses_events_dir, file_name), encoding="utf-8") as fh:
        ses_event = json.load(fh)
        ses_events.append(ses_event)


ses_events_dir = os.path.join(os.path.dirname(__file__), "zabbix_messages")
zabbix_events = []
for file_name in os.listdir(ses_events_dir):
    with open(os.path.join(ses_events_dir, file_name), encoding="utf-8") as fh:
        ses_event = json.load(fh)
        zabbix_events.append(ses_event)
