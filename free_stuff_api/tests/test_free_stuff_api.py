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
    free_item = FreeItem(None, None)
    free_item.__dict__ = {'name': 'Steinbach, MB',
                          'url': 'https://www.facebook.com/marketplace/item/1415801513621679/?ref=category_feed&referral_code=null&referral_story_type=listing&tracking=%7B%22qid%22%3A%22-7378121041319857739%22%2C%22mf_story_key%22%3A%2225215904178083416%22%2C%22commerce_rank_obj%22%3A%22%7B%5C%22target_id%5C%22%3A25215904178083416%2C%5C%22target_type%5C%22%3A0%2C%5C%22primary_position%5C%22%3A6%2C%5C%22ranking_signature%5C%22%3A1826639652643357917%2C%5C%22ranking_request_id%5C%22%3A152511885699243976%2C%5C%22commerce_channel%5C%22%3A504%2C%5C%22value%5C%22%3A0.00053615351725688%2C%5C%22candidate_retrieval_source_map%5C%22%3A%7B%5C%2225215904178083416%5C%22%3A3003%7D%7D%22%7D&__tn__=!%3AD', 'image_url': 'https://scontent-ord5-3.xx.fbcdn.net/v/t39.84726-6/637614859_1302615378293184_5630242580355385849_n.jpg?stp=c308.0.540.540a_dst-jpg_p180x540_tt6&_nc_cat=106&ccb=1-7&_nc_sid=92e707&_nc_ohc=oNaNzWhSEmwQ7kNvwGsgT3J&_nc_oc=AdnPGHJKtgdluFs_5WVCJKDuVrh9RVlfg-q93nlwa67InF9YDB9_ESfXbih8jjhBLzc&_nc_zt=14&_nc_ht=scontent-ord5-3.xx&_nc_gid=W_UUkKBmurFjuMWxhs-0lQ&oh=00_Afv_vkhSdQq4qHNQ8lpEB0rzqvVjt9DKgoKVlFCbmB4FWw&oe=699F8BF4',
                          'description': 'Steinbach, MB\nQueen frame'}
    assert free_stuff_api.notify_about_new_item(free_item)

@pytest.mark.unit
def test_provision_infra():
    free_stuff_api = FreeStuffAPI(config)
    assert free_stuff_api.provision_infra()


@pytest.mark.unit
def test_update():
    free_stuff_api = FreeStuffAPI(config)
    assert free_stuff_api.update()

@pytest.mark.wip
def test_main_free_stuff_mac_raw(free_stuff_mac_raw):
    assert free_stuff_mac_raw.main()

@pytest.mark.unit
def test_main_free_stuff_linux_amd_docker(linux_amd_docker):
    assert linux_amd_docker.main()

@pytest.mark.unit
def test_main_free_stuff_linux_arm_docker(linux_arm_docker):
    assert linux_arm_docker.main()

@pytest.mark.unit
def test_provision_db(free_stuff_mac_raw):
    assert free_stuff_mac_raw.provision_db()

@pytest.mark.unit
def test_add_platform(free_stuff_mac_raw):
    assert free_stuff_mac_raw.add_platform(Platform("Facebook"))
