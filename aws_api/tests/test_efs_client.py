"""
Test AWS client.

"""
import datetime

import pytest

# pylint: disable=missing-function-docstring

from horey.aws_api.aws_clients.efs_client import EFSClient
from horey.aws_api.aws_services_entities.efs_file_system import EFSFileSystem
from horey.aws_api.aws_services_entities.efs_access_point import EFSAccessPoint
from horey.aws_api.base_entities.region import Region
from horey.h_logger import get_logger

logger = get_logger()


@pytest.fixture(name="efs_client")
def fixture_efs_client(main_cache_dir_path):
    client = EFSClient()
    client.main_cache_dir_path = main_cache_dir_path
    return client


@pytest.fixture(name="file_system_src")
def fixture_file_system_src():
    file_system = EFSFileSystem({})
    file_system.region = Region.get_region("us-west-2")
    file_system.tags = [{"Key": "Name", "Value": "test"}]
    return file_system


@pytest.fixture(name="access_point_src")
def fixture_access_point_src(file_system_src, efs_client):
    efs_client.provision_file_system(file_system_src)
    access_point = EFSAccessPoint({})
    access_point.file_system_id = file_system_src.id
    access_point.region = file_system_src.region
    access_point.tags = [{"Key": "Name", "Value": "test"}]
    return access_point


@pytest.mark.done
def test_init_efs_client(efs_client):
    assert isinstance(efs_client, EFSClient)


@pytest.mark.done
def test_provision_and_dispose_file_system_raw(efs_client, file_system_src):
    request = {}

    response_create = efs_client.provision_file_system_raw(file_system_src.region, request)

    response_dispose = efs_client.dispose_file_system_raw(file_system_src.region, {"FileSystemId": response_create["FileSystemId"]})

    assert response_dispose


@pytest.mark.done
def test_provision_file_system_fail_no_tags(efs_client, file_system_src):
    file_system_src.tags = [{"Key": "Horey", "Value": "Horey"}]
    with pytest.raises(RuntimeError, match=".*No tag 'Name' associated.*"):
        efs_client.provision_file_system(file_system_src)


@pytest.mark.done
def test_provision_file_system_raw_with_tag_name(efs_client, file_system_src):
    request = {"Tags": file_system_src.tags}
    response_create = efs_client.provision_file_system_raw(file_system_src.region, request)
    assert response_create


@pytest.mark.done
def test_yield_file_systems_raw(efs_client, file_system_src):
    for dict_response in efs_client.yield_file_systems_raw(file_system_src.region):
        assert dict_response.get("FileSystemArn")
        assert dict_response.get("FileSystemId")


@pytest.mark.done
def test_yield_file_systems_region(efs_client, file_system_src):
    for file_system in efs_client.yield_file_systems(region=file_system_src.region):
        assert file_system.id
        assert file_system.arn
        assert file_system.region


@pytest.mark.done
def test_yield_file_systems(efs_client):
    for file_system in efs_client.yield_file_systems():
        assert file_system.id
        assert file_system.arn
        assert file_system.region


@pytest.mark.done
def test_update_file_system_information(efs_client, file_system_src):
    efs_client.update_file_system_information(file_system_src)
    assert file_system_src.id
    assert file_system_src.arn
    assert file_system_src.region


def delete_file_system(efs_client, file_system_src):
    """
    Use raw methods to delete file system.

    :param efs_client:
    :param file_system_src:
    :return:
    """

    efs_client.dispose_file_system_raw(file_system_src.region, {"FileSystemId": file_system_src.id})
    datetime_limit = datetime.datetime.now() + datetime.timedelta(minutes=10)
    while datetime.datetime.now() < datetime_limit:
        logger.info(f"Tests: updating status for efs file_system {file_system_src.id}")
        for response in efs_client.yield_file_systems_raw(file_system_src.region):
            if response["FileSystemId"] == file_system_src.id:
                break
        else:
            efs_client.clear_cache(EFSFileSystem)
            return True
    raise TimeoutError(f"Tests: updating status for efs file_system {file_system_src.id}")


@pytest.mark.done
def test_update_file_system_information_raises_no_tags_in_regional_file_system(efs_client, file_system_src):
    response_create = efs_client.provision_file_system_raw(file_system_src.region, {})
    file_system_src.id = response_create["FileSystemId"]

    with pytest.raises(RuntimeError, match=".*No tag 'Name' associated.*"):
        efs_client.update_file_system_information(file_system_src)
    delete_file_system(efs_client, file_system_src)


@pytest.mark.done
def test_provision_file_system_new_or_update(efs_client, file_system_src):
    assert efs_client.provision_file_system(file_system_src)


@pytest.mark.done
def test_provision_file_system_new(efs_client, file_system_src):
    efs_client.dispose_file_system(file_system_src)
    assert efs_client.provision_file_system(file_system_src)


@pytest.mark.done
def test_provision_file_system_update(efs_client, file_system_src: EFSFileSystem):
    efs_client.dispose_file_system(file_system_src)
    efs_client.provision_file_system(file_system_src)
    assert file_system_src.throughput_mode != "provisioned"
    assert file_system_src.provisioned_throughput_in_mibps != 10.0

    file_system_src.provisioned_throughput_in_mibps = 10.0
    file_system_src.throughput_mode = "provisioned"

    assert efs_client.provision_file_system(file_system_src)
    assert file_system_src.throughput_mode == "provisioned"
    assert file_system_src.provisioned_throughput_in_mibps == 10.0
    efs_client.dispose_file_system(file_system_src)


# Access point


@pytest.mark.done
def test_provision_and_dispose_access_point_raw(efs_client, access_point_src):
    request = {"FileSystemId": access_point_src.file_system_id}
    response_create = efs_client.provision_access_point_raw(access_point_src.region, request)

    response_dispose = efs_client.dispose_access_point_raw(access_point_src.region, {"AccessPointId": response_create["AccessPointId"]})

    assert response_dispose


@pytest.mark.done
def test_provision_access_point_raw_with_tag_name(efs_client, access_point_src):
    request = {"Tags": access_point_src.tags, "FileSystemId": access_point_src.file_system_id}
    response_create = efs_client.provision_access_point_raw(access_point_src.region, request)
    assert response_create


@pytest.mark.done
def test_yield_access_points_raw(efs_client, access_point_src):
    for dict_response in efs_client.yield_access_points_raw(access_point_src.region):
        assert dict_response.get("AccessPointId")
        assert dict_response.get("AccessPointArn")


@pytest.mark.done
def test_yield_access_points_region(efs_client, access_point_src):
    for access_point in efs_client.yield_access_points(region=access_point_src.region):
        assert access_point.id
        assert access_point.arn
        assert access_point.region


@pytest.mark.done
def test_yield_access_points(efs_client):
    for access_point in efs_client.yield_access_points():
        assert access_point.id
        assert access_point.arn
        assert access_point.region


@pytest.mark.done
def test_update_access_point_information(efs_client, access_point_src):
    efs_client.update_access_point_information(access_point_src)
    assert access_point_src.id
    assert access_point_src.arn
    assert access_point_src.region


@pytest.mark.done
def test_provision_access_point_fail_no_tags(efs_client, access_point_src):
    access_point_src.tags = [{"Key": "Horey", "Value": "Horey"}]
    with pytest.raises(RuntimeError, match=".*No tag 'Name' associated.*"):
        efs_client.provision_access_point(access_point_src)


def delete_access_point(efs_client, access_point_src):
    """
    Use raw methods to delete file system.

    :param efs_client:
    :param access_point_src:
    :return:
    """

    efs_client.dispose_access_point_raw(access_point_src.region, {"AccessPointId": access_point_src.id})
    datetime_limit = datetime.datetime.now() + datetime.timedelta(minutes=10)
    while datetime.datetime.now() < datetime_limit:
        logger.info(f"Tests: updating status for efs access_point {access_point_src.id}")
        for response in efs_client.yield_access_points_raw(access_point_src.region):
            if response["AccessPointId"] == access_point_src.id:
                break
        else:
            efs_client.clear_cache(EFSAccessPoint)
            return True
    raise TimeoutError(f"Tests: updating status for efs access_point {access_point_src.id}")


@pytest.mark.done
def test_update_access_point_information_raises_no_tags_in_regional_access_point(efs_client, access_point_src):
    response_create = efs_client.provision_access_point_raw(access_point_src.region,
                                                            {"FileSystemId": access_point_src.file_system_id})
    access_point_src.id = response_create["AccessPointId"]

    with pytest.raises(RuntimeError, match=".*No tag 'Name' associated.*"):
        efs_client.update_access_point_information(access_point_src)
    delete_access_point(efs_client, access_point_src)


@pytest.mark.done
def test_provision_access_point_new_or_update(efs_client, access_point_src):
    assert efs_client.provision_access_point(access_point_src)


@pytest.mark.done
def test_provision_access_point_new(efs_client, access_point_src):
    efs_client.dispose_access_point(access_point_src)
    assert efs_client.provision_access_point(access_point_src)
    assert access_point_src.id


@pytest.mark.done
def test_dispose_access_point(efs_client, access_point_src):
    assert efs_client.dispose_access_point(access_point_src)


@pytest.mark.done
def test_dispose_file_system(efs_client, file_system_src):
    assert efs_client.dispose_file_system(file_system_src)
