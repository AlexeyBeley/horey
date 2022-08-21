import pdb

from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup


def test_check_permissions_equal():
    sg = EC2SecurityGroup({})
    self_permission = {"FromPort": 8080, "IpProtocol": "tcp", "ToPort": 8080,
                       "IpRanges": [{"CidrIp": "1.1.1.1/32", "Description": "test"}]}
    target_permission = {"FromPort": 8080, "IpProtocol": "tcp", "ToPort": 8080, "IpRanges": [{"CidrIp": "1.1.1.1/32"}]}
    ret = sg.check_permissions_equal(self_permission, target_permission,
                                     check_without_description=True)
    assert ret


def test_generate_modify_ip_permissions_requests():
    sg_1 = EC2SecurityGroup({})
    sg_1.ip_permissions = [{"FromPort": 8080, "IpProtocol": "tcp", "ToPort": 8080,
                            "IpRanges": [{"CidrIp": "8.8.8.8/32", "Description": "test"}]}]
    sg_2 = EC2SecurityGroup({})
    sg_2.ip_permissions = [
        {"FromPort": 8080, "IpProtocol": "tcp", "ToPort": 8080, "IpRanges": [{"CidrIp": "8.8.8.8/32"}]}]
    add_request, revoke_request, update_description = sg_1.generate_modify_ip_permissions_requests(sg_2)
    assert add_request is None
    assert revoke_request is None
    assert update_description is not None


def test_generate_modify_ip_permissions_requests_2():
    sg_1 = EC2SecurityGroup({})
    sg_1.ip_permissions = [{"FromPort": 8080, "IpProtocol": "tcp",
                            "IpRanges": [{"CidrIp": "1.1.1.1/32", "Description": "test"},
                                         {"CidrIp": "1.1.1.3/32", "Description": "test"},
                                         {"CidrIp": "8.8.8.8/32", "Description": "test"}], "Ipv6Ranges": [],
                            "PrefixListIds": [], "ToPort": 8080, "UserIdGroupPairs": []}]
    sg_2 = EC2SecurityGroup({})
    sg_2.ip_permissions = [{"IpProtocol": "tcp", "FromPort": 8080, "ToPort": 8080,
                            "IpRanges": [{"CidrIp": "8.8.8.8/32", "Description": "test-1"}]},
                           {"IpProtocol": "tcp", "FromPort": 8080, "ToPort": 8080,
                            "IpRanges": [{"CidrIp": "1.1.1.1/32"}]},
                           {"IpProtocol": "tcp", "FromPort": 8080, "ToPort": 8080,
                            "IpRanges": [{"CidrIp": "1.1.1.2/32", "Description": "test"}]}]
    add_request, revoke_request, update_description = sg_1.generate_modify_ip_permissions_requests(sg_2)
    assert add_request == {"GroupId": None, "IpPermissions": [{"FromPort": 8080, "IpProtocol": "tcp", "ToPort": 8080,
                                                               "IpRanges": [
                                                                   {"CidrIp": "1.1.1.2/32", "Description": "test"}]}]}
    assert revoke_request == {"GroupId": None, "IpPermissions": [{"FromPort": 8080, "IpProtocol": "tcp", "ToPort": 8080,
                                                                  "IpRanges": [{"CidrIp": "1.1.1.3/32",
                                                                                "Description": "test"}]}]}
    assert update_description == {"GroupId": None, "IpPermissions": [
        {"FromPort": 8080, "IpProtocol": "tcp", "ToPort": 8080,
         "IpRanges": [{"CidrIp": "8.8.8.8/32", "Description": "test-1"}]},
        {"FromPort": 8080, "IpProtocol": "tcp", "ToPort": 8080, "IpRanges": [{"CidrIp": "1.1.1.1/32"}]}]}


if __name__ == "__main__":
    test_check_permissions_equal()
    test_generate_modify_ip_permissions_requests()
    test_generate_modify_ip_permissions_requests_2()
