"""
AWS clietn to handle service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
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
                self.get_session_client(region=self.get_region_from_arn(topic_arn)).publish, "MessageId",
                filters_req=filters_req
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
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            SNSSubscription,
                                                            update_info=update_info,
                                                            full_information_callback=full_information_callback,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def get_subscription_full_information(self, obj):
        """
        Standard.

        :param obj:
        :return:
        """

        if obj.arn in ["PendingConfirmation", "Deleted"]:
            return True

        for dict_src in self.execute(
                self.get_session_client(region=obj.region).get_subscription_attributes,
                None,
                raw_data=True,
                filters_req={"SubscriptionArn": obj.arn},
        ):
            obj.attributes = dict_src["Attributes"]
        return True

    def yield_subscriptions_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).list_subscriptions, "Subscriptions", filters_req=filters_req
        )

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
                self.get_session_client(region=subscription.region).get_subscription_attributes,
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
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            SNSTopic,
                                                            update_info=update_info,
                                                            full_information_callback=full_information_callback,
                                                            get_tags_callback=lambda topic: self.get_tags(topic,
                                                                                                          function=self.get_session_client(
                                                                                                              region=region).list_tags_for_resource) if get_tags else None,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_topics_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).list_topics, "Topics", filters_req=filters_req
        )

    def get_all_topics(self, region=None, full_information=True):
        """
        Get all topics in all regions.
        :return:
        """

        return list(self.yield_topics(region=region, full_information=full_information))

    def get_region_topics(self, region, full_information=True, get_tags=True):
        """
        Standard.

        :param get_tags:
        :param region:
        :param full_information:
        :return:
        """

        return list(self.yield_topics(region=region, full_information=full_information, get_tags=get_tags))

    def get_topic_full_information(self, topic):
        """
        Standard.

        :param topic:
        :return:
        """

        dict_src = self.execute_with_single_reply(
            self.get_session_client(region=topic.region).get_topic_attributes,
            None,
            raw_data=True,
            filters_req={"TopicArn": topic.arn},
        )

        topic.attributes = dict_src["Attributes"]

        for dict_src in self.execute(
                self.get_session_client(region=topic.region).get_data_protection_policy,
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
            for _topic in self.get_region_topics(topic.region, full_information=False, get_tags=False):
                if _topic.name == topic.name:
                    topic.arn = _topic.arn
                    break
            else:
                return False

        if not full_information:
            return True

        logger.info(f"Fetching sns topic information: {topic.arn}")
        dict_src = self.execute_with_single_reply(
            self.get_session_client(region=topic.region).get_topic_attributes,
            None,
            raw_data=True,
            filters_req={"TopicArn": topic.arn},
        )

        topic.attributes = dict_src["Attributes"]

        topic.tags = self.get_tags(topic, function=self.get_session_client(region=topic.region).list_tags_for_resource)
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
                self.tag_resource_raw(topic.region, update_tags)
            topic.update_from_attrs(region_topic)
        else:
            response = self.provision_topic_raw(topic.region, topic.generate_create_request())
            topic.update_from_raw_response(response)

    def provision_topic_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """
        logger.info(f"Creating topic: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_topic, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(SNSTopic)
            del response["ResponseMetadata"]

            return response

    def tag_resource_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """

        logger.info(f"Tagging resource: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).tag_resource, None, raw_data=True, filters_req=request_dict
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

        response = self.provision_subscription_raw(subscription.region,
                                                   subscription.generate_create_request()
                                                   )
        subscription.update_from_raw_response(response)

    def provision_subscription_raw(self, region, request_dict):
        """
        Standard.

        :param request_dict:
        :return:
        """
        logger.info(f"Creating subscription: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).subscribe, None, raw_data=True, filters_req=request_dict
        ):
            del response["ResponseMetadata"]
            return response
