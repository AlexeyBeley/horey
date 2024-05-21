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



# SES
SES configuration set has SNS topic to notify all events it supports:
bounce, reject, open, click etc.
Alert system will handle Production SES events, the "lambda-self" events and SES notification channel events.

Possible Dimensions:
'Send',
'Delivery',
'Bounce',
'Open',


'PublishSuccess',
* https://docs.aws.amazon.com/ses/latest/dg/receiving-email-metrics.html
* 'Name': 'RuleSetName'
* 'Name': 'RuleName'


'PublishExpired'
* https://docs.aws.amazon.com/ses/latest/dg/receiving-email-metrics.html
* 'Name': 'RuleSetName'
* 'Name': 'RuleName'


'Received',
* https://docs.aws.amazon.com/ses/latest/dg/receiving-email-metrics.html
* 'Name': 'RuleSetName'
* 'Name': 'RuleName'


'PublishFailure':
* https://docs.aws.amazon.com/ses/latest/dg/receiving-email-metrics.html
* 'Name': 'RuleSetName'
* 'Name': 'RuleName'


'Reputation.BounceRate'
* https://docs.aws.amazon.com/ses/latest/dg/reputationdashboardmessages.html
* 'Name': 'ses:configuration-set'


'Reputation.ComplaintRate'
* https://docs.aws.amazon.com/ses/latest/dg/reputationdashboardmessages.html
* 'Name': 'ses:configuration-set'


'Reputation.DeliveriesEligibleForBounceRate'
* https://docs.aws.amazon.com/ses/latest/dg/reputationdashboardmessages.html
* 'Name': 'ses:configuration-set'

HOREY_SES_eventType_DeliveryDelay

Package usage:
* User configures which configuration set to monitor. (product_config_sets)


* Alert system provisions SNS topic to receive SNS topic alerts (alert_system_sns_topic)
* Alert system provisions Lambda to print SES related logs in Cloudwatch logs (alert_system_lambda)
* Alert system provisions SES configuration set be used by SES notification channel (alert_system_config_set)
* Alert system provisions cloudwatch metric filters on (product_config_sets), (alert_system_config_set) and (alert_system_lambda) Invoke a Lambda function-> (alert_system_lambda)


* User configures his configuration set to send notifications to Alert System's SNS topic


DeliveryDelay notification
# https://docs.aws.amazon.com/ses/latest/dg/event-publishing-retrieving-sns-contents.html#event-publishing-retrieving-sns-contents-delivery-delay-object


# todo:
* Create send_email function that inserts "{{ses:openTracker}}" at the beginning of the email.
* Make send_email to use alert_system_config set in case no other used.
* Make sure all configuration sets have alert system sns_topic destination configured and there are permissions 