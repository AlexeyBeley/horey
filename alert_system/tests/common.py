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


zabbix_events_dir = os.path.join(os.path.dirname(__file__), "zabbix_messages")
zabbix_events = []
for file_name in os.listdir(zabbix_events_dir):
    with open(os.path.join(zabbix_events_dir, file_name), encoding="utf-8") as fh:
        ses_event = json.load(fh)
        zabbix_events.append(ses_event)


cloudwatch_events_dir = os.path.join(os.path.dirname(__file__), "cloudwatch_messages")
cloudwatch_events = []
for file_name in os.listdir(cloudwatch_events_dir):
    with open(os.path.join(cloudwatch_events_dir, file_name), encoding="utf-8") as fh:
        ses_event = json.load(fh)
        cloudwatch_events.append(ses_event)

cloudwatch_events_dir = os.path.join(os.path.dirname(__file__), "malformed_cloudwatch_messages")
malformed_cloudwatch_events = []
for file_name in os.listdir(cloudwatch_events_dir):
    with open(os.path.join(cloudwatch_events_dir, file_name), encoding="utf-8") as fh:
        ses_event = json.load(fh)
        malformed_cloudwatch_events.append(ses_event)


events_dir = os.path.join(os.path.dirname(__file__), "self_monitoring_valid_events")
self_monitoring_valid_events = []
for file_name in os.listdir(events_dir):
    with open(os.path.join(events_dir, file_name), encoding="utf-8") as fh:
        ses_event = json.load(fh)
        self_monitoring_valid_events.append(ses_event)


cloudwatch_direct_alarm_eventss_dir = os.path.join(os.path.dirname(__file__), "cloudwatch_messages")
cloudwatch_direct_alarm_eventss = []
for file_name in os.listdir(cloudwatch_direct_alarm_eventss_dir):
    with open(os.path.join(cloudwatch_direct_alarm_eventss_dir, file_name), encoding="utf-8") as fh:
        ses_event = json.load(fh)
        cloudwatch_direct_alarm_eventss.append(ses_event)

cloudwatch_direct_alarm_events_dir = os.path.join(os.path.dirname(__file__), "postgres_direct_lambda_alarm_events")
cloudwatch_direct_alarm_events = []
for file_name in os.listdir(cloudwatch_direct_alarm_events_dir):
    with open(os.path.join(cloudwatch_direct_alarm_events_dir, file_name), encoding="utf-8") as fh:
        ses_event = json.load(fh)
        cloudwatch_direct_alarm_events.append(ses_event)

