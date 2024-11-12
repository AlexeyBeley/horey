"""
AWS client to handle service API requests.
"""

from horey.aws_api.aws_clients.boto3_client import Boto3Client
from horey.aws_api.aws_services_entities.wafv2_ip_set import WAFV2IPSet
from horey.aws_api.aws_services_entities.wafv2_web_acl import WAFV2WebACL
from horey.h_logger import get_logger

logger = get_logger()


class WAFV2Client(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    NEXT_PAGE_REQUEST_KEY = "Marker"
    NEXT_PAGE_RESPONSE_KEY = "NextMarker"

    def __init__(self):
        client_name = "wafv2"
        super().__init__(client_name)

    def provision_ip_set(self, ip_set: WAFV2IPSet):
        """
        Standard

        @param ip_set:
        @return:
        """
        logger.info("Provisioning ip set: " + ip_set.get_tag("Name", casesensitive=True))
        current_ip_set = WAFV2IPSet({})
        current_ip_set.region = ip_set.region
        current_ip_set.name = ip_set.name
        current_ip_set.scope = ip_set.scope

        if not self.update_ip_set_information(current_ip_set):
            response = self.provision_ip_set_raw(ip_set.region, ip_set.generate_create_request())
            dict_src = response["Summary"]
            return ip_set.update_from_raw_response(dict_src)

        ip_set.id = current_ip_set.id
        ip_set.lock_token = current_ip_set.lock_token
        request = current_ip_set.generate_update_request(ip_set)
        if request:
            response = self.update_ip_set_raw(ip_set.region, request)
            assert response.get("NextLockToken")

        return self.update_ip_set_information(ip_set)

    def update_ip_set_information(self, ip_set: WAFV2IPSet):
        """
        Update info.

        :param ip_set:
        :return:
        """

        if not ip_set.id:
            filters_req = {"Scope": ip_set.scope}
            for current_ip_set in self.yield_ip_sets(ip_set.region, filters_req=filters_req):
                if ip_set.name == current_ip_set.name:
                    if not ip_set.update_from_attrs(current_ip_set):
                        raise RuntimeError(f"Can not update ip set with name: {ip_set.name}")
                    break
            else:
                return False

        filters_req = {"Scope": ip_set.scope, "Name": ip_set.name, "Id": ip_set.id}
        for response in self.execute(
                self.get_session_client(region=ip_set.region).get_ip_set, None, raw_data=True,
                filters_req=filters_req
            ):
            dict_src = response["IPSet"]
            dict_src["Scope"] = filters_req["Scope"]
            dict_src["LockToken"] = response["LockToken"]
            return ip_set.update_from_raw_response(dict_src)
        return False

    def provision_ip_set_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Creating ip set: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).create_ip_set, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(WAFV2IPSet)
            return response

    def update_ip_set_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Updating ip set: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).update_ip_set, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(WAFV2IPSet)
            return response

    def yield_ip_sets(self, region=None, update_info=False, filters_req=None):
        """
        Yield objects

        :return:
        """

        regional_fetcher_generator = self.yield_ip_sets_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            WAFV2IPSet,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_ip_sets_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        if filters_req is None:
            filters_req = {}

        if "Scope" in filters_req:
            scopes = [filters_req["Scope"]]
        else:
            scopes = ["REGIONAL"]
            if region.region_mark == "us-east-1":
                scopes.append("CLOUDFRONT")

        for scope in scopes:
            filters_req["Scope"] = scope
            for response in self.execute(
                    self.get_session_client(region=region).list_ip_sets, "IPSets",
                    filters_req=filters_req
            ):
                response["Scope"] = filters_req["Scope"]
                yield response

    def dispose_ip_set(self, ip_set: WAFV2IPSet):
        """
        Standard.

        @param ip_set:
        @return:
        """

        if not self.update_ip_set_information(ip_set):
            return True

        self.dispose_ip_set_raw(ip_set.region, ip_set.generate_dispose_request())
        self.clear_cache(WAFV2IPSet)
        return True

    def dispose_ip_set_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Deleting ip set: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).delete_ip_set, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(WAFV2IPSet)
            return response

    def yield_web_acls(self, region=None, update_info=False, filters_req=None):
        """
        Yield objects

        :return:
        """

        regional_fetcher_generator = self.yield_web_acls_raw
        yield from self.regional_service_entities_generator(regional_fetcher_generator,
                                                            WAFV2WebACL,
                                                            update_info=update_info,
                                                            regions=[region] if region else None,
                                                            filters_req=filters_req)

    def yield_web_acls_raw(self, region, filters_req=None):
        """
        Yield dictionaries.

        :return:
        """

        if filters_req is None:
            filters_req = {}

        if "Scope" in filters_req:
            scopes = [filters_req["Scope"]]
        else:
            scopes = ["REGIONAL"]
            if region.region_mark == "us-east-1":
                scopes.append("CLOUDFRONT")

        for scope in scopes:
            filters_req["Scope"] = scope
            for response in self.execute(
                    self.get_session_client(region=region).list_web_acls, "WebACLs",
                    filters_req=filters_req
            ):
                response["Scope"] = filters_req["Scope"]
                yield response

    def provision_web_acl_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Creating web acl: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).create_web_acl, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(WAFV2WebACL)
            return response

    def update_web_acl_information(self, web_acl: WAFV2WebACL):
        """
        Update info.

        :param web_acl:
        :return:
        """

        if not web_acl.id:
            filters_req = {"Scope": web_acl.scope}
            for current_web_acl in self.yield_web_acls(web_acl.region, filters_req=filters_req):
                if web_acl.name == current_web_acl.name:
                    if not web_acl.update_from_attrs(current_web_acl):
                        raise RuntimeError(f"Can not update ip set with name: {web_acl.name}")
                    break
            else:
                return False

        filters_req = {"Scope": web_acl.scope, "Name": web_acl.name, "Id": web_acl.id}
        for response in self.execute(
                self.get_session_client(region=web_acl.region).get_web_acl, None, raw_data=True,
                filters_req=filters_req
            ):
            dict_src = response["WebACL"]
            dict_src["Scope"] = filters_req["Scope"]
            dict_src["LockToken"] = response["LockToken"]
            return web_acl.update_from_raw_response(dict_src)
        return False

    def dispose_web_acl_raw(self, region, request_dict):
        """
        Standard.

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Deleting web acl: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).delete_web_acl, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(WAFV2WebACL)
            return response

    def provision_web_acl(self, web_acl:WAFV2WebACL):
        """
        Standard

        @param web_acl:
        @return:
        """
        logger.info("Provisioning ip set: " + web_acl.get_tag("Name", casesensitive=True))
        current_web_acl = WAFV2WebACL({})
        current_web_acl.region = web_acl.region
        current_web_acl.name = web_acl.name
        current_web_acl.scope = web_acl.scope

        if not self.update_web_acl_information(current_web_acl):
            response = self.provision_web_acl_raw(web_acl.region, web_acl.generate_create_request())
            dict_src = response["Summary"]
            return web_acl.update_from_raw_response(dict_src)

        web_acl.id = current_web_acl.id
        web_acl.lock_token = current_web_acl.lock_token
        request = current_web_acl.generate_update_request(web_acl)
        if request:
            response = self.update_web_acl_raw(web_acl.region, request)
            assert response.get("NextLockToken")

        return self.update_web_acl_information(web_acl)

    def update_web_acl_raw(self, region, request_dict):
        """
        Standard

        :param region:
        :param request_dict:
        :return:
        """

        logger.info(f"Updating web acl: {request_dict}")

        for response in self.execute(
                self.get_session_client(region=region).update_web_acl, None, raw_data=True, filters_req=request_dict
        ):
            self.clear_cache(WAFV2WebACL)
            return response
