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

        if self.configuration.hosted_zone_name:
            hosted_zone = self.get_hosted_zone(self.configuration.hosted_zone_name)
        else:
            hosted_zone = self.find_appropriate_hosted_zone()

        if "elb.amazonaws.com" in self.configuration.dns_target:
            if hosted_zone.config["PrivateZone"]:
                raise NotImplementedError(hosted_zone.config["PrivateZone"], self.configuration.dns_target)
            dict_record = {
                "Name": self.configuration.dns_address,
                "Type": "A",
                "AliasTarget":
                    {"HostedZoneId": self.environment_api.aws_api.elbv2_client.HOSTED_ZONES[self.environment_api.configuration.region],
                     "DNSName": f"dualstack.{self.configuration.dns_target}",
                     "EvaluateTargetHealth": False
                     }
            }
        else:
            raise RuntimeError(self.configuration.dns_target)

        record = HostedZone.Record(dict_record)
        hosted_zone.records.append(record)
        self.environment_api.aws_api.route53_client.upsert_resource_record_sets(hosted_zone)

        return True

    def get_hosted_zone(self, hz_name):
        """
        Standard.

        :param hz_name:
        :return:
        """

        hosted_zone = HostedZone({})
        hosted_zone.name = hz_name
        if not self.environment_api.aws_api.route53_client.update_hosted_zone_information(hosted_zone):
            raise RuntimeError(f"Was not able to find hosted zone: '{hz_name}'")

        return hosted_zone

    def find_appropriate_hosted_zone(self):
        """
        Analyze the hosted zones and find the best matching.

        :return:
        """

        lst_ret = []
        lst_dns = self.configuration.dns_address.split(".")
        for i in range(0, len(lst_dns)):
            hosted_zone = HostedZone({})
            hosted_zone.name = ".".join(lst_dns[i:])
            if self.environment_api.aws_api.route53_client.update_hosted_zone_information(hosted_zone):
                lst_ret.append(hosted_zone)

        logger.info(f"Found following hosted zones: {[_hz.name for _hz in lst_ret]}")
        return lst_ret[0]

    def update(self):
        """

        :return:
        """

        breakpoint()