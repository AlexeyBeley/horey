import pdb

from horey.aws_api.aws_clients.events_client import EventsClient
from horey.aws_api.aws_services_entities.event_bridge_rule import EventBridgeRule
from horey.aws_api.aws_services_entities.event_bridge_target import EventBridgeTarget
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.base_entities.region import Region

AWSAccount.set_aws_region(Region.get_region("us-west-2"))


def test_init_lambda_client():
    assert isinstance(EventsClient(), EventsClient)


def test_get_region_events():
    events_client = EventsClient()
    region_rules = events_client.get_region_rules(Region.get_region("us-east-1"))
    assert isinstance(region_rules, list)


def test_provision_rule():
    rule = EventBridgeRule({})
    rule.name = "rule-alexey-test-trigger-lambda"
    rule.description = "rule-alexey-test-trigger-lambda"
    rule.region = Region.get_region("us-west-2")
    rule.schedule_expression = "rate(1 minute)"
    rule.event_bus_name = "default"
    rule.state = "ENABLED"
    rule.tags = [
        {
            'Key': 'string',
            'Value': 'string'
        },
    ]

    target = EventBridgeTarget({})
    target.id = "test-alexey-target"
    target.arn = "arn:aws:lambda:us-west-2:xxxxxx:function:horey-test-lambda"

    rule.targets = [target]
    client = EventsClient()
    client.provision_rule(rule)

    

if __name__ == "__main__":
    #test_init_lambda_client()
    #test_get_region_events()
    test_provision_rule()
