"""
AWS clietn to handle service API requests.
"""
import pdb

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.sns_subscription import SNSSubscription
from horey.aws_api.aws_services_entities.sns_topic import SNSTopic
from horey.h_logger import get_logger

logger = get_logger()


class SNSClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        client_name = "sns"
        super().__init__(client_name)

    def raw_publish(self, topic_arn, subject, message):
        filters_req = {"TopicArn": topic_arn, "Message": ":exclamation:" + message, "Subject": subject}
        # state_dict = {"Ok": ":thumbsup:", "Info": ":information_source:", "Severe": ":exclamation:"}

        for response in self.execute(self.client.publish, "MessageId", filters_req=filters_req):
            return response

    def get_all_subscriptions(self, region=None, full_information=True):
        """
        Get all subscriptions in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_subscriptions(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_subscriptions(region, full_information=full_information)

        return final_result

    def get_region_subscriptions(self, region, full_information=True):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.list_subscriptions, "Subscriptions"):
            obj = SNSSubscription(dict_src)
            final_result.append(obj)
            if full_information:
                if obj.arn == "PendingConfirmation":
                    continue
                self.update_subscription_information(obj)

        return final_result

    def update_subscription_information(self, subscription):
        for dict_src in self.execute(self.client.get_subscription_attributes, None, raw_data=True,
                                     filters_req={"SubscriptionArn": subscription.arn}):
            subscription.attributes = dict_src["Attributes"]

    def get_all_topics(self, region=None, full_information=True):
        """
        Get all topics in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_topics(region, full_information=full_information)

        final_result = list()
        for region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_topics(region, full_information=full_information)

        return final_result

    def get_region_topics(self, region, full_information=True):
        final_result = list()
        AWSAccount.set_aws_region(region)
        for dict_src in self.execute(self.client.list_topics, "Topics"):
            obj = SNSTopic(dict_src)
            final_result.append(obj)
            if full_information:
                self.update_topic_information(obj)

        return final_result

    def update_topic_information(self, topic):
        if topic.arn is None:
            for _topic in self.get_region_topics(topic.region):
                if _topic.name == topic.name:
                    topic.arn = _topic.arn
                    break
            else:
                return False

        dict_src = self.execute_with_single_reply(self.client.get_topic_attributes, None, raw_data=True,
                                                  filters_req={"TopicArn": topic.arn})

        topic.attributes = dict_src["Attributes"]

        topic.tags = self.get_tags(topic, function=self.client.list_tags_for_resource)
        return True

    def provision_topic(self, topic):
        region_topic = SNSTopic({})
        region_topic.region = topic.region
        region_topic.name = topic.name
        if self.update_topic_information(region_topic):
            topic.update_from_raw_response(region_topic.dict_src)

        AWSAccount.set_aws_region(topic.region)
        response = self.provision_topic_raw(topic.generate_create_request())
        topic.update_from_raw_response(response)

    def provision_topic_raw(self, request_dict):
        logger.info(f"Creating topic: {request_dict}")
        for response in self.execute(self.client.create_topic, None, raw_data=True,
                                     filters_req=request_dict):
            del response["ResponseMetadata"]

            return response

    def provision_subscription(self, subscription: SNSSubscription):
        region_subscriptions = self.get_region_subscriptions(subscription.region)
        for region_subscription in region_subscriptions:
            if region_subscription.endpoint == subscription.endpoint and \
                    region_subscription.topic_arn == subscription.topic_arn:
                subscription.update_from_raw_response(region_subscription.dict_src)
                return

        AWSAccount.set_aws_region(subscription.region)
        response = self.provision_subscription_raw(subscription.generate_create_request())
        subscription.update_from_raw_response(response)

    def provision_subscription_raw(self, request_dict):
        logger.info(f"Creating subscription: {request_dict}")
        for response in self.execute(self.client.subscribe, None, raw_data=True,
                                     filters_req=request_dict):
            del response["ResponseMetadata"]
            return response
