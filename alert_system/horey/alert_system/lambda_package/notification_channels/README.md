Self testing

1. Monitored_log_group filters pattern "ERROR"
2. In case occurs > 1, trigger alarm
3. Alarm triggers alert_system_lambda with: log_group_name, pattern.
4. Notification channel "notification_channel_echo" prints the pattern

We want to test a log line containing the patter triggers notification in the notification channel.



Cloudwatch event 