


todo:
ec2-instance, ecs-service, lambda - full iam access.

todo: reachability report: h_flow.

todo: expired certificates in RDS

todo: too old ecr images - older then a year can be deleted.
todo: too big ecr images.

lambda no cloudwatch alarms
ecs no cloudwatch alarms


security:
lambda:InvokeFunction on "*" or region == *
If created using infrastructure as a code, development role gets access to prod functions.
