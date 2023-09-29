# Serverless alert system 


production_service--.\
↓###################↓\
Cloudwatch Logs  -> Metric -> Alarm -> SNS -> AlertSystemLambda.\
↑                   ↑_________________________↓                |\
|______________________________________________________________↓

Components:
alert_system - provisions all parts of the system, provides testing functionality.

lambda_package - files used in the AlertSystemLambda to handle notifications.
message_dispatcher- Dispatches various messages from multiple sources: Cloudwatch, Opensearch etc.
notification_channel - a user facing destinations to send the messages to. 

Both message_dispatcher and notification_channel are implementation specific: you can use the base implementation
but better overwriting them with your own to customize the message appearance and notification destinations. 

