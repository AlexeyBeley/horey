# Serverless alert system 

<pre>
Grafana--------------------------------------╮
Opensearch----------------------------╮      |
Production_service-╮                  |      |
|                  |                  |      |
V                  V                  V      V
Cloudwatch Logs -> Metric -> Alarm -> SNS -> AlertSystemLambda╮
^                  ^                         |                |
|                  ╰-------------------------╯                |
╰-------------------------------------------------------------╯

* Grafana: Triggers Lambda directly from a Bash script using AWS CLI.
* Opensearch: Monitor alert sends notification to SNS topic.
* Production_service: Writes logs to Cloudwatch Logs service and sends metrics to the Cloudwatch service.
* AlertSystemLambda: Writes logs to Cloudwatch Logs service and sends metrics to the Cloudwatch service.
</pre>

Components:
alert_system - provisions all parts of the system, provides testing functionality.

lambda_package - files used in the AlertSystemLambda to handle notifications.
message_dispatcher- Dispatches various messages from multiple sources: Cloudwatch, Opensearch etc.
notification_channel - a user facing destinations to send the messages to. 

Both message_dispatcher and notification_channel are implementation specific: you can use the base implementation
but better overwriting them with your own to customize the message appearance and notification destinations. 
