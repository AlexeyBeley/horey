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
                    "Key": "Name",
                    "Value": "Horey"
                },
            ],
            "FileSystemProtection": {
                "ReplicationOverwriteProtection": "ENABLED"
            }}


@pytest.mark.done
def test_init(dict_src):
    self = EFSFileSystem(dict_src)
    assert self.id == "id:mock"
    assert self.arn == "arn:mock"


@pytest.mark.done
def test_update_from_raw_response():
    self = EFSFileSystem({})
    assert self.update_from_raw_response({"AvailabilityZoneId": "new_id"})
    assert self.availability_zone_id == "new_id"


@pytest.mark.done
def test_update_from_raw_response_wrong_key():
    self = EFSFileSystem({})
    assert not self.update_from_raw_response({"Horey": "Horey"})


@pytest.mark.done
def test_generate_create_request(dict_src):
    self = EFSFileSystem(dict_src)

    request = self.generate_create_request()
    assert request == {
        "ThroughputMode": "bursting",
        "ProvisionedThroughputInMibps": 123.0,
        "Encrypted": True,
        "Tags": [{"Key": "Name", "Value": "Horey"}]
    }


@pytest.mark.done
def test_generate_create_request_empty(dict_src):
    del dict_src["ThroughputMode"]
    del dict_src["ProvisionedThroughputInMibps"]
    del dict_src["Encrypted"]
    self = EFSFileSystem(dict_src)

    request = self.generate_create_request()
    assert request == {"Tags": [{"Key": "Name", "Value": "Horey"}]}


@pytest.mark.done
def test_generate_create_request_raise_no_tagname(dict_src):
    del dict_src["ThroughputMode"]
    del dict_src["ProvisionedThroughputInMibps"]
    del dict_src["Encrypted"]
    del dict_src["Tags"]
    self = EFSFileSystem(dict_src)
    with pytest.raises(RuntimeError, match=".*No tag 'Name' associated.*"):
        self.generate_create_request()


@pytest.mark.done
def test_generate_dispose_request(dict_src):
    self = EFSFileSystem(dict_src)
    request = self.generate_dispose_request()
    assert request == {"FileSystemId": "id:mock"}


@pytest.mark.done
def test_generate_update_request_no_change(dict_src):
    self = EFSFileSystem(dict_src)
    other = EFSFileSystem(dict_src)
    assert self.generate_update_request(other) is None


@pytest.mark.done
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


@pytest.mark.done
def test_get_tag_casesensitive_true_little():
    dict_src = {"Tags": [
        {
            "Key": "horey",
            "Value": "string1"
        },
    ]}
    self = EFSFileSystem(dict_src)
    assert self.get_tag("horey", casesensitive=True)


@pytest.mark.done
def test_get_tag_casesensitive_true_little_raises():
    dict_src = {"Tags": [
        {
            "Key": "Horey",
            "Value": "string1"
        },
    ]}

    self = EFSFileSystem(dict_src)
    with pytest.raises(RuntimeError, match=".*No tag 'horey' associated.*"):
        self.get_tag("horey", casesensitive=True)


@pytest.mark.done
def test_get_tag_raises_no_tags():
    self = EFSFileSystem({})
    with pytest.raises(RuntimeError, match=".*No tag 'horey' associated.*"):
        self.get_tag("horey")


@pytest.mark.done
def test_get_tagname_raises_ignore_missing_tag():
    self = EFSFileSystem({})
    with pytest.raises(ValueError, match=".*Should not set.*"):
        self.get_tagname(ignore_missing_tag=True)


@pytest.mark.done
def test_get_status_raise():
    self = EFSFileSystem({})
    with pytest.raises(self.UndefinedStatusError, match=".*life_cycle_state was not set.*"):
        self.get_status()


@pytest.mark.done
def test_get_status_raise_unsupported_status():
    self = EFSFileSystem({})
    self.life_cycle_state = "new_status"
    with pytest.raises(KeyError, match=".*new_status.*"):
        self.get_status()


@pytest.mark.done
@pytest.mark.parametrize("status", ["creating", "available", "updating", "deleting", "deleted", "error"])
def test_get_status_correct(status):
    self = EFSFileSystem({})
    self.life_cycle_state = status
    assert self.get_status().name == status.upper()
