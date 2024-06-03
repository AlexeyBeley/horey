"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.aws_services_entities.sesv2_account import SESV2Account
from horey.aws_api.aws_services_entities.sesv2_email_identity import SESV2EmailIdentity
from horey.aws_api.aws_services_entities.sesv2_email_template import SESV2EmailTemplate
from horey.aws_api.aws_services_entities.sesv2_configuration_set import (
    SESV2ConfigurationSet,
)

from horey.h_logger import get_logger

logger = get_logger()


class SESV2Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    UNSUPPORTED_REGIONS = ["ap-east-1", "ap-southeast-3"]

    def __init__(self):
        client_name = "sesv2"
        super().__init__(client_name)

    # pylint: disable= too-many-arguments
    def yield_accounts(self, region=None, update_info=False, filters_req=None):
        """
        Yield accounts

        :return:
        """

        regional_fetcher_generator = self.yield_accounts_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            SESV2Account,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_accounts_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=region).get_account, None, raw_data=True, filters_req=filters_req
        ):
            del dict_src["ResponseMetadata"]
            yield dict_src

    # pylint: disable= too-many-arguments
    def yield_email_identities(self, region=None, update_info=False, filters_req=None):
        """
        Yield email_identities

        :return:
        """

        regional_fetcher_generator = self.yield_email_identities_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            SESV2EmailIdentity,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_email_identities_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for email_identity_dict in self.execute(
                self.get_session_client(region=region).list_email_identities, "EmailIdentities", filters_req=filters_req
        ):
            response = list(
                self.execute(
                    self.get_session_client(region=region).get_email_identity,
                    None,
                    raw_data=True,
                    filters_req={"EmailIdentity": email_identity_dict["IdentityName"]},
                    exception_ignore_callback=lambda x: "NotFoundException" in repr(x),
                )
            )
            if len(response) == 0:
                return

            if len(response) > 1:
                raise RuntimeError(f"Expected to find <= 1 but found {len(response)}")

            dict_src = response[0]
            del dict_src["ResponseMetadata"]
            dict_src.update(email_identity_dict)

            yield dict_src

    def get_all_email_identities(self, region=None):
        """
        Get all email_identities in all regions.
        :return:
        """

        return list(self.yield_email_identities(region=region))

    def get_region_email_identities(self, region):
        """
        Standard

        @param region:
        @return:
        """

        if region.region_mark in self.UNSUPPORTED_REGIONS:
            return []

        logger.info(f"get_region_email_identities: {region.region_mark}")
        return list(self.yield_email_identities(region=region))

    def update_email_identity_information(self, obj: SESV2EmailIdentity):
        """
        Standard

        @param obj:
        @return:
        """

        response = list(
            self.execute(
                self.get_session_client(region=obj.region).get_email_identity,
                None,
                raw_data=True,
                filters_req={"EmailIdentity": obj.name},
                exception_ignore_callback=lambda x: "NotFoundException" in repr(x),
            )
        )
        if len(response) == 0:
            return

        if len(response) > 1:
            raise RuntimeError(f"Expected to find <= 1 but found {len(response)}")

        dict_src = response[0]
        del dict_src["ResponseMetadata"]

        obj.update_from_raw_response(dict_src)

    # pylint: disable= too-many-arguments
    def yield_configuration_sets(self, region=None, update_info=False, full_information=True, filters_req=None):
        """
        Yield configuration_sets

        :return:
        """

        full_information_callback = self.get_configuration_set_full_information if full_information else None
        regional_fetcher_generator = self.yield_configuration_sets_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            SESV2ConfigurationSet,
                                                            update_info=update_info,
                                                            full_information_callback=full_information_callback,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_configuration_sets_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        for name in self.execute(
                self.get_session_client(region=region).list_configuration_sets, "ConfigurationSets",
                filters_req=filters_req
        ):
            dict_src = list(
                self.execute(
                    self.get_session_client(region=region).get_configuration_set,
                    None,
                    raw_data=True,
                    filters_req={"ConfigurationSetName": name},
                )
            )[0]
            del dict_src["ResponseMetadata"]
            yield dict_src

    def get_all_configuration_sets(self, region=None, full_information=False):
        """
        Get all configuration_sets in all regions.

        :return:
        """

        return list(self.yield_configuration_sets(region=region, full_information=full_information))

    def get_region_configuration_sets(self, region, full_information=False):
        """
        Standard

        @param region:
        @param full_information:
        @return:
        """

        return list(self.yield_configuration_sets(region=region, full_information=full_information))

    def get_configuration_set_full_information(self, obj):
        """
        Standard.

        :param obj: 
        :return: 
        """
        obj.event_destinations = []
        for response in self.execute(
                self.get_session_client(region=obj.region).get_configuration_set_event_destinations,
                None,
                raw_data=True,
                filters_req={"ConfigurationSetName": obj.name},
        ):
            if "EventDestinations" in response:
                obj.event_destinations += response["EventDestinations"]

    # pylint: disable= too-many-arguments
    def yield_email_templates(self, region=None, update_info=False, full_information=True, filters_req=None):
        """
        Yield email_templates

        :return:
        """

        full_information_callback = self.get_email_template_full_information if full_information else None
        regional_fetcher_generator = self.yield_email_templates_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            SESV2EmailTemplate,
                                                            update_info=update_info,
                                                            full_information_callback=full_information_callback,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_email_templates_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        yield from self.execute(
            self.get_session_client(region=region).list_email_templates, "TemplatesMetadata", filters_req=filters_req
        )

    def get_all_email_templates(self, region=None, full_information=True):
        """
        Get all email_templates in all regions.

        :return:
        """
        return list(self.yield_email_templates(region=region, full_information=full_information))

    def get_region_email_templates(self, region, full_information=True):
        """
        Standard

        @param region:
        @param full_information:
        @return:
        """

        return list(self.yield_email_templates(region=region, full_information=full_information))

    def get_email_template_full_information(self, obj: SESV2EmailTemplate):
        """
        Standard

        @param obj:
        @return:
        """

        dict_src = list(
            self.execute(
                self.get_session_client(region=obj.region).get_email_template,
                None,
                raw_data=True,
                filters_req={"TemplateName": obj.name},
            )
        )[0]
        del dict_src["ResponseMetadata"]

        obj.update_from_raw_response(dict_src)

    def provision_configuration_set(self, configuration_set: SESV2ConfigurationSet):
        """
        Standard

        @param configuration_set:
        @return:
        """

        region_configuration_sets = self.get_region_configuration_sets(
            configuration_set.region
        )
        for region_configuration_set in region_configuration_sets:
            if region_configuration_set.name == configuration_set.name:
                configuration_set.update_from_raw_response(
                    region_configuration_set.dict_src
                )
                self.get_configuration_set_full_information(region_configuration_set)
                break
        else:
            region_configuration_set = None
            self.provision_configuration_set_raw(configuration_set.region,
                                                 configuration_set.generate_create_request()
                                                 )
        create_requests = configuration_set.generate_create_requests_event_destinations(region_configuration_set)
        for create_request in create_requests:
            self.create_request_event_destination_raw(configuration_set.region, create_request)

    def provision_configuration_set_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """

        logger.info(f"Creating configuration_set: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_configuration_set,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            self.clear_cache(SESV2ConfigurationSet)
            return response

    def create_request_event_destination_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        :param region:
        """

        logger.info(f"Creating configuration_set event_destination: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_configuration_set_event_destination,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            self.clear_cache(SESV2ConfigurationSet)
            return response

    def update_email_template_information(self, email_template: SESV2EmailTemplate):
        """
        Standard

        :param email_template:
        :return:
        """

        for region_template in self.yield_email_templates(email_template.region, full_information=True):
            if region_template.name == email_template.name:
                email_template.update_from_attrs(region_template)
                return True
        return False

    def provision_email_template(self, email_template: SESV2EmailTemplate):
        """
        Standard

        @param email_template:
        @return:
        """

        current_template = SESV2EmailTemplate({"TemplateName": email_template.name})
        current_template.region = email_template.region
        if self.update_email_template_information(current_template):
            update_request = current_template.generate_update_request(current_template)
            if update_request:
                self.update_email_template_raw(current_template.region, update_request)
        else:
            self.create_email_template_raw(current_template.region, email_template.generate_create_request())

        self.update_email_template_information(email_template)
        return True

    def update_email_template_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        :param region:
        """

        for response in self.execute(
                self.get_session_client(region=region).update_email_template,
                None,
                raw_data=True,
                filters_req=request_dict,
                exception_ignore_callback=lambda x: "NotFoundException" in repr(x),
        ):
            logger.info(f"Updated email_template: {request_dict}")
            return response
        return True

    def create_email_template_raw(self, region, request_dict):
        """
        Create email template

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Creating email_template: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_email_template,
                None,
                raw_data=True,
                filters_req=request_dict,
                exception_ignore_callback=lambda x: "NotFoundException" in repr(x),
        ):
            return response
        return True

    def provision_email_identity(self, email_identity: SESV2EmailIdentity):
        """
        Standard

        @param email_identity:
        @return:
        """
        self.update_email_identity_information(email_identity)

        if email_identity.identity_type is not None:
            return

        response = self.provision_email_identity_raw(email_identity.region,
                                                     email_identity.generate_create_request()
                                                     )
        email_identity.update_from_raw_response(response)

    def provision_email_identity_raw(self, region, request_dict):
        """
        Standard

        @param request_dict:
        @return:
        """

        logger.info(f"Creating email_identity: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_email_identity,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            del response["ResponseMetadata"]
            return response

    def get_region_suppressed_destinations(
            self, region, custom_filter=None, full_information=None
    ):
        """
        Get list of all suppressed destinations.

        @param region:
        @param custom_filter:
        @param full_information:
        @return:
        """
        logger.info(f"list_suppressed_destinations in region {region.region_mark}")

        ret = []
        for response in self.execute(
                self.get_session_client(region=region).list_suppressed_destinations,
                "SuppressedDestinationSummaries",
                filters_req=custom_filter,
        ):

            if full_information:
                full_info_custom_filter = {"EmailAddress": response["EmailAddress"]}
                for full_information_response in self.execute(
                        self.get_session_client(region=region).get_suppressed_destination,
                        "SuppressedDestination",
                        filters_req=full_info_custom_filter,
                ):
                    ret.append(full_information_response)
            else:
                ret.append(response)

        return ret

    def send_email_raw(self, region, request_dict):
        """
        Send an email.

        :return:
        """

        for response in self.execute(
                self.get_session_client(region=region).send_email,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            del response["ResponseMetadata"]
            conf_set_name = request_dict.get("ConfigurationSetName")
            if conf_set_name:
                log_message = f"Email sent: from '{request_dict.get('FromEmailAddress')}', to " \
                              f"'{request_dict.get('Destination')}', message_id: '{response.get('MessageId')}', " \
                              f"configuration set: '{conf_set_name}'"
            else:
                log_message = f"Email sent: from '{request_dict.get('FromEmailAddress')}', to " \
                              f"'{request_dict.get('Destination')}', message_id: '{response.get('MessageId')}'"

            logger.info(log_message)
            return response
