"""
Testing service entity

"""

import pytest
from horey.aws_api.aws_services_entities.efs_file_system import EFSFileSystem

# pylint: disable = missing-function-docstring


@pytest.fixture(name="dict_src")
def fixture_dict_src():
    return {"OwnerId": "string",
                "CreationToken": "string",
                "FileSystemId": "id:mock",
                "FileSystemArn": "arn:mock",
                "CreationTime": "",
                "LifeCycleState": "",
                "Name": "string",
                "NumberOfMountTargets": 123,
                "SizeInBytes": None,
                "PerformanceMode": None,
                "Encrypted": True,
                "KmsKeyId": "string",
                "ThroughputMode": "bursting",
                "ProvisionedThroughputInMibps": 123.0,
                "AvailabilityZoneName": "string",
                "AvailabilityZoneId": "string",
                "Tags": [
                    {
                        "Key": "string",
                        "Value": "string"
                    },
                ],
                "FileSystemProtection": {
                    "ReplicationOverwriteProtection": "ENABLED"
                }}


@pytest.mark.wip
def test_init(dict_src):
    self = EFSFileSystem(dict_src)
    assert self.id == "id:mock"
    assert self.arn == "arn:mock"


@pytest.mark.wip
def test_update_from_raw_response():
    self = EFSFileSystem({})
    assert self.update_from_raw_response({"AvailabilityZoneId": "new_id"})
    assert self.availability_zone_id == "new_id"


@pytest.mark.wip
def test_update_from_raw_response_wrong_key():
    self = EFSFileSystem({})
    assert not self.update_from_raw_response({"Horey": "Horey"})


@pytest.mark.wip
def test_generate_create_request(dict_src):

    self = EFSFileSystem(dict_src)

    request = self.generate_create_request()
    assert request == {"FileSystemId": "id:mock", "ThroughputMode": "bursting", "ProvisionedThroughputInMibps":123.0}


@pytest.mark.wip
def test_generate_create_request_partial(dict_src):
    del dict_src["ThroughputMode"]
    del dict_src["ProvisionedThroughputInMibps"]
    self = EFSFileSystem(dict_src)

    request = self.generate_create_request()
    assert request == {"FileSystemId": "id:mock"}


@pytest.mark.wip
def test_generate_dispose_request(dict_src):
    self = EFSFileSystem(dict_src)
    request = self.generate_dispose_request()
    assert request == {"FileSystemId": "id:mock"}


@pytest.mark.wip
def test_generate_update_request_no_change(dict_src):
    self = EFSFileSystem(dict_src)
    other = EFSFileSystem(dict_src)
    assert self.generate_update_request(other) is None


@pytest.mark.wip
def test_generate_update_request_with_change(dict_src):
    self = EFSFileSystem(dict_src)
    dict_src["Tags"] = [
                    {
                        "Key": "string",
                        "Value": "string1"
                    },
                ]
    dict_src["ThroughputMode"] = "provisioned"
    other = EFSFileSystem(dict_src)
    request = self.generate_update_request(other)
    assert request == {"FileSystemId": "id:mock", "ThroughputMode": "provisioned"}
