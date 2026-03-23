"""
Testing selenium api
"""
from pathlib import Path

import pytest
from horey.free_stuff_api.free_stuff_api import FreeStuffAPIConfigurationPolicy, FreeStuffAPI

from horey.common_utils.free_item import FreeItem
from horey.free_stuff_api.platform import Platform

config = FreeStuffAPIConfigurationPolicy()
config.configuration_file_full_path = Path(__file__).parent.parent.parent.parent / "ignore" / "test_frs_api_configuration.py"
config.horey_directory_path =  Path(__file__).parent.parent.parent
config.init_from_file()
config.db_file_path = Path("/opt/hfrs/hfrs.sqlite")



# pylint: disable= missing-function-docstring

@pytest.fixture(scope="module", name="free_stuff_mac_raw")
def fixture_free_stuff_mac_raw():
    free_stuff_api = FreeStuffAPI(config)
    yield free_stuff_api
    free_stuff_api.selenium_api.disconnect()

@pytest.fixture(scope="module", name="linux_amd_docker")
def fixture_linux_amd_docker():
    free_stuff_api = FreeStuffAPI(config)
    yield free_stuff_api
    free_stuff_api.selenium_api.disconnect()


@pytest.fixture(scope="module", name="linux_arm_docker")
def fixture_linux_arm_docker():
    free_stuff_api = FreeStuffAPI(config)
    config.chromedriver_path = Path("/opt/chrome-driver/chromedriver")
    config.chrome_path = Path("/opt/chrome/chrome")
    yield free_stuff_api
    free_stuff_api.selenium_api.disconnect()

@pytest.mark.unit
def test_main():
    free_stuff_api = FreeStuffAPI(config)
    assert free_stuff_api.main()


@pytest.mark.unit
def test_add_free_item_to_db():
    free_stuff_api = FreeStuffAPI(config)
    free_item = FreeItem("name", "url")
    assert free_stuff_api.add_free_item_to_db(free_item)

@pytest.mark.unit
def test_notify_about_new_item():

    free_stuff_api = FreeStuffAPI(config)
    url = 'https://www.facebook.com/marketplace/item/951081683937401/?ref=category_feed&referral_code=null&referral_story_type=listing&tracking=%7B%22qid%22%3A%22-7208799824235551155%22%2C%22mf_story_key%22%3A%2226591833053762219%22%2C%22commerce_rank_obj%22%3A%22%7B%5C%22target_id%5C%22%3A26591833053762219%2C%5C%22target_type%5C%22%3A0%2C%5C%22primary_position%5C%22%3A36%2C%5C%22ranking_signature%5C%22%3A5258348999073026090%2C%5C%22ranking_request_id%5C%22%3A907753257306275608%2C%5C%22commerce_channel%5C%22%3A504%2C%5C%22value%5C%22%3A0.010212191960216%2C%5C%22candidate_retrieval_source_map%5C%22%3A%7B%5C%2226591833053762219%5C%22%3A3001%7D%7D%22%7D&__tn__=!%3AD'
    image_url = 'https://scontent-ord5-2.xx.fbcdn.net/v/t39.84726-6/655689552_2096376911202768_5175015685651605039_n.jpg?stp=c0.87.526.526a_dst-jpg_p526x395_tt6&_nc_cat=103&ccb=1-7&_nc_sid=92e707&_nc_ohc=ohuQ_BIylTsQ7kNvwE9l7n4&_nc_oc=Adp85U_yKavgCJ8TR5m_8I_jgBGXxKD41x0i08zHAW6fA0gwl0WA7K4HP2UwmrOfsyI&_nc_zt=14&_nc_ht=scontent-ord5-2.xx&_nc_gid=Upe7bcFcJ5AzRRVLGeyEOQ&_nc_ss=7a30f&oh=00_AfwHui_aKVKaDF6THy2XB4Kr9oj70oOUdXlSkDgcufoIeg&oe=69C5136E'
    description = "test description"
    free_item = FreeItem("test", url, image_url=image_url, description=description)
    assert free_stuff_api.notify_about_new_item(free_item)

@pytest.mark.unit
def test_provision_infra():
    free_stuff_api = FreeStuffAPI(config)
    assert free_stuff_api.provision_infra()


@pytest.mark.unit
def test_update():
    free_stuff_api = FreeStuffAPI(config)
    assert free_stuff_api.update()


@pytest.mark.unit
def test_provision_db(free_stuff_mac_raw):
    assert free_stuff_mac_raw.provision_db()

@pytest.mark.unit
def test_add_platform(free_stuff_mac_raw):
    assert free_stuff_mac_raw.add_platform(Platform(None,"Facebook"))

@pytest.mark.unit
def test_delete_platform_items(free_stuff_mac_raw):
    assert free_stuff_mac_raw.delete_platform_items(free_stuff_mac_raw.platforms[0])


@pytest.mark.wip
def test_main_free_stuff_mac_raw(free_stuff_mac_raw):
    assert free_stuff_mac_raw.main()

@pytest.mark.unit
def test_main_free_stuff_linux_amd_docker(linux_amd_docker):
    assert linux_amd_docker.main()

@pytest.mark.unit
def test_main_free_stuff_linux_arm_docker(linux_arm_docker):
    assert linux_arm_docker.main()


