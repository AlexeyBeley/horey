"""
Testing service entity

"""

import pytest
from horey.aws_api.aws_services_entities.efs_access_point import EFSAccessPoint


# pylint: disable = missing-function-docstring


@pytest.fixture(name="dict_src")
def fixture_dict_src():
    return {
        "ClientToken": "string",
        "Name": "string",
        "Tags": [
            {
                "Key": "Horey",
                "Value": "Horey"
            },
        ],
        "AccessPointId": "id:mock",
        "AccessPointArn": "arn:mock",
        "FileSystemId": "file_system_id:mock",
        "PosixUser": {
            "Uid": 123,
            "Gid": 123,
            "SecondaryGids": [
                123,
            ]
        },
        "RootDirectory": {
            "Path": "string",
            "CreationInfo": {
                "OwnerUid": 123,
                "OwnerGid": 123,
                "Permissions": "string"
            }
        },
        "OwnerId": "string",
        "LifeCycleState": "creating"
    }


@pytest.mark.done
def test_init(dict_src):
    self = EFSAccessPoint(dict_src)
    assert self.id == "id:mock"
    assert self.arn == "arn:mock"


@pytest.mark.done
def test_update_from_raw_response():
    self = EFSAccessPoint({})
    assert self.update_from_raw_response({"RootDirectory": "new_root_dir"})
    assert self.root_directory == "new_root_dir"


@pytest.mark.done
def test_update_from_raw_response_wrong_key():
    self = EFSAccessPoint({})
    assert not self.update_from_raw_response({"Horey": "Horey"})


@pytest.mark.done
def test_generate_create_request(dict_src):
    self = EFSAccessPoint(dict_src)
    self.tags = [{"Key": "Name", "Value": "Horey"}]

    request = self.generate_create_request()
    assert request == {"FileSystemId": "file_system_id:mock", "Tags": [{"Key": "Name", "Value": "Horey"}],
                       "RootDirectory": {"Path": "string",
                                         "CreationInfo": {"OwnerUid": 123, "OwnerGid": 123, "Permissions": "string"}},
                       "PosixUser": {"Uid": 123, "Gid": 123, "SecondaryGids": [123]}, "ClientToken": "string"}


@pytest.mark.done
def test_generate_create_request_raise_no_tagname(dict_src):
    del dict_src["Tags"]
    self = EFSAccessPoint(dict_src)
    with pytest.raises(RuntimeError, match=".*No tag 'Name' associated.*"):
        self.generate_create_request()


@pytest.mark.done
def test_generate_dispose_request(dict_src):
    self = EFSAccessPoint(dict_src)
    request = self.generate_dispose_request()
    assert request == {"AccessPointId": "id:mock"}


@pytest.mark.done
def test_get_tag_casesensitive_true_little():
    dict_src = {"Tags": [
        {
            "Key": "horey",
            "Value": "string1"
        },
    ]}
    self = EFSAccessPoint(dict_src)
    assert self.get_tag("horey", casesensitive=True)


@pytest.mark.done
def test_get_tag_casesensitive_true_little_raises():
    dict_src = {"Tags": [
        {
            "Key": "Horey",
            "Value": "string1"
        },
    ]}

    self = EFSAccessPoint(dict_src)
    with pytest.raises(RuntimeError, match=".*No tag 'horey' associated.*"):
        self.get_tag("horey", casesensitive=True)


@pytest.mark.done
def test_get_tag_raises_no_tags():
    self = EFSAccessPoint({})
    with pytest.raises(RuntimeError, match=".*No tag 'horey' associated.*"):
        self.get_tag("horey")


@pytest.mark.done
def test_get_tagname_raises_ignore_missing_tag():
    self = EFSAccessPoint({})
    with pytest.raises(ValueError, match=".*Should not set.*"):
        self.get_tagname(ignore_missing_tag=True)


@pytest.mark.done
def test_get_status_raise():
    self = EFSAccessPoint({})
    with pytest.raises(self.UndefinedStatusError, match=".*life_cycle_state was not set.*"):
        self.get_status()


@pytest.mark.done
def test_get_status_raise_unsupported_status():
    self = EFSAccessPoint({})
    self.life_cycle_state = "new_status"
    with pytest.raises(KeyError, match=".*new_status.*"):
        self.get_status()


@pytest.mark.done
@pytest.mark.parametrize("status", ["creating", "available", "updating", "deleting", "deleted", "error"])
def test_get_status_correct(status):
    self = EFSAccessPoint({})
    self.life_cycle_state = status
    assert self.get_status().name == status.upper()
