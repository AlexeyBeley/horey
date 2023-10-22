"""
AWS clietn to handle service API requests.
"""

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
        """
        Publish message string.

        :param topic_arn:
        :param subject:
        :param message:
        :return:
        """

        filters_req = {
            "TopicArn": topic_arn,
            "Message": message,
            "Subject": subject,
        }
        # state_dict = {"Ok": ":thumbsup:", "Info": ":information_source:", "Severe": ":exclamation:"}

        for response in self.execute(
            self.client.publish, "MessageId", filters_req=filters_req
        ):
            return response

    # pylint: disable= too-many-arguments
    def yield_subscriptions(self, region=None, update_info=False, full_information=True, filters_req=None):
        """
        Yield subscriptions

        :return:
        """

        full_information_callback = self.get_subscription_full_information if full_information else None
        regional_fetcher_generator = self.yield_subscriptions_raw
        for certificate in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  SNSSubscription,
                                                  update_info=update_info,
                                                  full_information_callback= full_information_callback,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield certificate

    def get_subscription_full_information(self, obj):
        """
        Standard.

        :param obj:
        :return:
        """

        if obj.arn in ["PendingConfirmation", "Deleted"]:
            return True

        for dict_src in self.execute(
            self.client.get_subscription_attributes,
            None,
            raw_data=True,
            filters_req={"SubscriptionArn": obj.arn},
        ):
            obj.attributes = dict_src["Attributes"]
        return True

    def yield_subscriptions_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.list_subscriptions, "Subscriptions", filters_req=filters_req
        ):
            yield dict_src

    def get_all_subscriptions(self, region=None, full_information=True):
        """
        Get all subscriptions in all regions.
        :return:
        """

        return list(self.yield_subscriptions(region=region, full_information=full_information))

    def get_region_subscriptions(self, region, full_information=True):
        """
        Standard.

        :param region:
        :param full_information:
        :return:
        """

        return list(self.yield_subscriptions(region=region, full_information=full_information))

    def update_subscription_information(self, subscription):
        """
        Standard.

        :param subscription:
        :return:
        """

        logger.info(
            f"Updating subscription information: 'SubscriptionArn': '{subscription.arn}'"
        )

        for dict_src in self.execute(
            self.client.get_subscription_attributes,
            None,
            raw_data=True,
            filters_req={"SubscriptionArn": subscription.arn},
        ):
            subscription.attributes = dict_src["Attributes"]

    # pylint: disable= too-many-arguments
    def yield_topics(self, region=None, update_info=False, full_information=True, filters_req=None, get_tags=True):
        """
        Yield topics

        :return:
        """

        full_information_callback = self.get_topic_full_information if full_information else None
        regional_fetcher_generator = self.yield_topics_raw
        for certificate in self.regional_service_entities_generator(regional_fetcher_generator,
                                                  SNSTopic,
                                                  update_info=update_info,
                                                  full_information_callback= full_information_callback,
                                                  get_tags_callback=lambda topic: self.get_tags(topic, function=self.client.list_tags_for_resource) if get_tags else None,
                                                  regions=[region] if region else None,
                                                  filters_req=filters_req):
            yield certificate

    def yield_topics_raw(self, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.client.list_topics, "Topics", filters_req=filters_req
        ):
            yield dict_src

    def get_all_topics(self, region=None, full_information=True):
        """
        Get all topics in all regions.
        :return:
        """

        return list(self.yield_topics(region=region, full_information=full_information))

    def get_region_topics(self, region, full_information=True):
        """
        Standard.

        :param region:
        :param full_information:
        :return:
        """

        return list(self.yield_topics(region=region, full_information=full_information))

    def get_topic_full_information(self, topic):
        """
        Standard.

        :param topic:
        :return:
        """

        dict_src = self.execute_with_single_reply(
            self.client.get_topic_attributes,
            None,
            raw_data=True,
            filters_req={"TopicArn": topic.arn},
        )

        topic.attributes = dict_src["Attributes"]

        for dict_src in self.execute(
                    self.client.get_data_protection_policy,
                    "DataProtectionPolicy",
                    filters_req={"ResourceArn": topic.arn},
            ):
            topic.data_protection_policy = dict_src

    def update_topic_information(self, topic, full_information=True):
        """
        Standard.

        :param full_information:
        :param topic:
        :return:
        """

        if topic.arn is None:
            for _topic in self.get_region_topics(topic.region, full_information=False):
                if _topic.name == topic.name:
                    topic.arn = _topic.arn
                    break
            else:
                return False

        if not full_information:
            return True

        dict_src = self.execute_with_single_reply(
            self.client.get_topic_attributes,
            None,
            raw_data=True,
            filters_req={"TopicArn": topic.arn},
        )

        topic.attributes = dict_src["Attributes"]

        topic.tags = self.get_tags(topic, function=self.client.list_tags_for_resource)
        return True

    def provision_topic(self, topic: SNSTopic):
        """
        Standard.

        :param topic:
        :return:
        """

        region_topic = SNSTopic({})
        region_topic.region = topic.region
        region_topic.name = topic.name
        if self.update_topic_information(region_topic):
            update_tags = region_topic.generate_tag_resource_request(topic)
            if update_tags:
                self.clear_cache(SNSTopic)
                self.tag_resource_raw(update_tags)
            topic.update_from_raw_response(region_topic.dict_src)
        else:
            AWSAccount.set_aws_region(topic.region)
            response = self.provision_topic_raw(topic.generate_create_request())
            topic.update_from_raw_response(response)

    def provision_topic_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """
        logger.info(f"Creating topic: {request_dict}")
        for response in self.execute(
            self.client.create_topic, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(SNSTopic)
            del response["ResponseMetadata"]

            return response


    def tag_resource_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Tagging resource: {request_dict}")

        for response in self.execute(
            self.client.tag_resource, None, raw_data=True, filters_req=request_dict
        ):
            del response["ResponseMetadata"]

            return response

    def provision_subscription(self, subscription: SNSSubscription):
        """
        Standard.

        :param subscription:
        :return:
        """
        region_subscriptions = self.get_region_subscriptions(subscription.region, full_information=False)
        for region_subscription in region_subscriptions:
            if (
                region_subscription.endpoint == subscription.endpoint
                and region_subscription.topic_arn == subscription.topic_arn
            ):
                subscription.update_from_raw_response(region_subscription.dict_src)
                self.get_subscription_full_information(subscription)
                return

        AWSAccount.set_aws_region(subscription.region)
        response = self.provision_subscription_raw(
            subscription.generate_create_request()
        )
        subscription.update_from_raw_response(response)

    def provision_subscription_raw(self, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """
        logger.info(f"Creating subscription: {request_dict}")
        for response in self.execute(
            self.client.subscribe, None, raw_data=True, filters_req=request_dict
        ):
            del response["ResponseMetadata"]
            return response
