"""
Standard Load balancing maintainer.

"""

from horey.h_logger import get_logger
from horey.aws_api.aws_services_entities.route53_hosted_zone import HostedZone


logger = get_logger()


class DNSAPI:
    """
    Manage ECS.

    """

    def __init__(self, configuration, environment_api):
        self.configuration = configuration
        self.environment_api = environment_api

    def provision(self):
        """
        Provision ECS infrastructure.

        :return:
        """
        breakpoint()
        dict_record = {
            "Name": self,
            "Type": "A",
            "AliasTarget":
                {"HostedZoneId": self.aws_api.elbv2_client.HOSTED_ZONES[self.configuration.region],
                 "DNSName": f"dualstack.{load_balancer.dns_name}",
                 "EvaluateTargetHealth": False
                 }
        }
        try:
            self.dns_api.configuration.hosted_zone_name
        except self.dns_api.configuration.UndefinedValueError:
            self.dns_api.find_appropriate_hosted_zone()
        return True

    def find_appropriate_hosted_zone(self):

            # todo: move to dns_api
            breakpoint()
            lst_dns = self.dns_api.configuration.service_address.split(".")
            for i in range(0, len(lst_dns)):
                hosted_zone = HostedZone({})
                hosted_zone.name = lst_dns[i:].join(".")
                if self.environment_api.aws_api.route53_client.update_hosted_zone_information(self, hosted_zone):
                    lst_ret.append(hosted_zone)

            self.dns_api.configuration.hosted_zone_name = ""

    def update(self):
        """

        :return:
        """

        breakpoint()
