"""
Ec2 security group unit tests.

"""

from horey.aws_api.aws_services_entities.ec2_security_group import EC2SecurityGroup


def test_check_permissions_equal():
    """
    Check check_without_description flag is working.

    @return:
    """
    sg = EC2SecurityGroup({})
    self_permission = {
        "FromPort": 8080,
        "IpProtocol": "tcp",
        "ToPort": 8080,
        "IpRanges": [{"CidrIp": "1.1.1.1/32", "Description": "test"}],
    }
    target_permission = {
        "FromPort": 8080,
        "IpProtocol": "tcp",
        "ToPort": 8080,
        "IpRanges": [{"CidrIp": "1.1.1.1/32"}],
    }
    ret = sg.check_permissions_equal(
        self_permission, target_permission, check_without_description=True
    )
    assert ret


def test_generate_modify_ip_permissions_requests():
    """
    Check description change.

    @return:
    """

    sg_1 = EC2SecurityGroup({})
    sg_1.ip_permissions = [
        {
            "FromPort": 8080,
            "IpProtocol": "tcp",
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "8.8.8.8/32", "Description": "test"}],
        }
    ]
    sg_2 = EC2SecurityGroup({})
    sg_2.ip_permissions = [
        {
            "FromPort": 8080,
            "IpProtocol": "tcp",
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "8.8.8.8/32"}],
        }
    ]
    (
        add_request,
        revoke_request,
        update_description,
    ) = sg_1.generate_modify_ip_permissions_requests(sg_2)
    assert add_request is None
    assert revoke_request is None
    assert update_description is not None


def test_generate_modify_ip_permissions_requests_2():
    """
    Check different changes in one request.

    @return:
    """

    sg_1 = EC2SecurityGroup({})
    sg_1.ip_permissions = [
        {
            "FromPort": 8080,
            "IpProtocol": "tcp",
            "IpRanges": [
                {"CidrIp": "1.1.1.1/32", "Description": "test"},
                {"CidrIp": "1.1.1.3/32", "Description": "test"},
                {"CidrIp": "8.8.8.8/32", "Description": "test"},
            ],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "ToPort": 8080,
            "UserIdGroupPairs": [],
        }
    ]
    sg_2 = EC2SecurityGroup({})
    sg_2.ip_permissions = [
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "8.8.8.8/32", "Description": "test-1"}],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "1.1.1.1/32"}],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "1.1.1.2/32", "Description": "test"}],
        },
    ]
    (
        add_request,
        revoke_request,
        update_description,
    ) = sg_1.generate_modify_ip_permissions_requests(sg_2)
    assert add_request == {
        "GroupId": None,
        "IpPermissions": [
            {
                "FromPort": 8080,
                "IpProtocol": "tcp",
                "ToPort": 8080,
                "IpRanges": [{"CidrIp": "1.1.1.2/32", "Description": "test"}],
            }
        ],
    }
    assert revoke_request == {
        "GroupId": None,
        "IpPermissions": [
            {
                "FromPort": 8080,
                "IpProtocol": "tcp",
                "ToPort": 8080,
                "IpRanges": [{"CidrIp": "1.1.1.3/32", "Description": "test"}],
            }
        ],
    }
    assert update_description == {
        "GroupId": None,
        "IpPermissions": [
            {
                "FromPort": 8080,
                "IpProtocol": "tcp",
                "ToPort": 8080,
                "IpRanges": [{"CidrIp": "8.8.8.8/32", "Description": "test-1"}],
            },
            {
                "FromPort": 8080,
                "IpProtocol": "tcp",
                "ToPort": 8080,
                "IpRanges": [{"CidrIp": "1.1.1.1/32"}],
            },
        ],
    }


def test_generate_modify_ip_permissions_requests_no_ip_ranges():
    """
    Check different types of location.

    @return:
    """
    sg_1 = EC2SecurityGroup({})
    sg_1.ip_permissions = [
        {
            "FromPort": 8080,
            "IpProtocol": "tcp",
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "1.1.1.1/32", "Description": "Test descr"}],
        }
    ]
    sg_2 = EC2SecurityGroup({})
    sg_2.ip_permissions = [
        {
            "FromPort": 8080,
            "IpProtocol": "tcp",
            "ToPort": 8080,
            "PrefixListIds": [{"PrefixListId": "pl-1111111111111111"}],
        }
    ]

    (
        add_request,
        revoke_request,
        update_description,
    ) = sg_1.generate_modify_ip_permissions_requests(sg_2)

    assert add_request == {
        "GroupId": None,
        "IpPermissions": [
            {
                "FromPort": 8080,
                "IpProtocol": "tcp",
                "ToPort": 8080,
                "PrefixListIds": [{"PrefixListId": "pl-1111111111111111"}],
            }
        ],
    }
    assert revoke_request == {
        "GroupId": None,
        "IpPermissions": [
            {
                "FromPort": 8080,
                "IpProtocol": "tcp",
                "ToPort": 8080,
                "IpRanges": [{"CidrIp": "1.1.1.1/32", "Description": "Test descr"}],
            }
        ],
    }
    assert update_description is None


def test_split_permissions():
    """
    Test split All permissions.

    @return:
    """

    src_permissions = [
        {
            "IpProtocol": "-1",
            "IpRanges": [{"CidrIp": "1.1.1.1/32", "Description": "1111 description"}],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
        }
    ]
    permissions = EC2SecurityGroup.split_permissions(src_permissions)
    assert len(permissions) == 1


if __name__ == "__main__":
    test_check_permissions_equal()
    test_generate_modify_ip_permissions_requests()
    test_generate_modify_ip_permissions_requests_2()
    test_generate_modify_ip_permissions_requests_no_ip_ranges()
    test_split_permissions()
