
from horey.common_utils.common_utils import CommonUtils


def main(selenium_api):
    FacebookAPI = CommonUtils.load_object_from_module_raw("/Users/alexeybeley/git/horey/facebook_api/horey/facebook_api/facebook_api.py", "FacebookAPI")

    fb_api = FacebookAPI(None)
    fb_api._selenium_api = selenium_api

    return fb_api.main()
