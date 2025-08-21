Event handling

1. Event- AWS Lambda event as received by handler. No limit on the structure.
2. EventHandler Receives the event and passes it to Message Factory
3. Message Factory is configured using lambda_package_configuration_policy - e.g. dynamic message types
4. generates message according to static or dynamic message types.
5. EventHandler then moves the message to MessageDispatcher.
6. MessageDispatcher is generating notification channels using NotificationChannelFactory
7. NotificationChannelFactory uses lambda_package_configuration_policy to initialize notification channels.
8. MessageDispatcher uses Message.generate_notification interface to generate a notification according to the message implementation.
9. MessageDispatcher goes over notification channels and notifies them.



Lambda package has to be tested locally before deploying in Lambda:
that means all permissions needed by lambda should be in the deployer:
ses send mail etc.
