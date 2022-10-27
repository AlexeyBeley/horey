"""
Testing gitlab api functionality.

"""
import json
import os
import pytest

from horey.jenkins_manager.authorization_job.authorization_applicator import AuthorizationApplicator
from horey.jenkins_manager.authorization_job.authorization_job import AuthorizationJob
from horey.jenkins_manager.authorization_job.authorization_job_configuration_policy import \
    AuthorizationJobConfigurationPolicy

from horey.common_utils.common_utils import CommonUtils

mock_values_file_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ignore", "mock_values.py"))
mock_values = CommonUtils.load_object_from_module(mock_values_file_path, "main")


# pylint: disable=missing-function-docstring

configuration = AuthorizationJobConfigurationPolicy()
configuration.authorization_map_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "authorization_map.json")
authorization_job = AuthorizationJob(configuration)


@pytest.mark.skip(reason="Can not test")
def test_authorization_applicator_serialize():
    restrictions = [{
                "name": "var_1",
                "value": "val_1",
                "required": True
            }]
    dict_src = {"job_name": "job_name",
                "user_identity": "user_identity",
                "parameters_restrictions": restrictions}
    rule = AuthorizationApplicator.Rule(dict_src)
    authorization_applicator = AuthorizationApplicator()
    authorization_applicator.append_rule(rule)
    authorization_applicator.serialize(configuration.authorization_map_file_path)

@pytest.mark.skip(reason="Can not test")
def test_authorization_applicator_deserialize():
    authorization_applicator = AuthorizationApplicator()
    authorization_applicator.deserialize(configuration.authorization_map_file_path)


@pytest.mark.skip(reason="Can not test")
def test_authorization_applicator_request_init():
    request = AuthorizationApplicator.Request(json.dumps({"job_name": "job_name", "parameters": {"var_1": "val_1"}, "user_identity": "user_identity"}))
    assert request.job_name == "job_name"
    assert request.parameters == {"var_1": "val_1"}
    assert request.user_identity == "user_identity"


@pytest.mark.skip(reason="Can not test")
def test_authorization_applicator_request_init_special_chars():
    request = AuthorizationApplicator.Request('{"user_identity": "john.doe horey_special_char_replacement_lessjohn.doe@gmail.comhorey_special_char_replacement_more", "job_name": "job_name", "parameters": {"var_1": "val_1"}}')
    assert request.job_name == "job_name"
    assert request.parameters == {"var_1": "val_1"}
    assert request.user_identity == "john.doe <john.doe@gmail.com>"


@pytest.mark.skip(reason="Can not test")
def test_authorization_applicator_request_serialize():
    request = AuthorizationApplicator.Request('{}')
    request.job_name = "job_name"
    request.parameters = {"var_1": "val_1"}
    request.user_identity = "user_identity"
    assert json.loads(request.serialize()) == {"job_name": "job_name", "parameters": {"var_1": "val_1"}, "user_identity": "user_identity"}


@pytest.mark.skip(reason="Can not test")
def test_authorization_applicator_request_serialize_special_chars():
    request = AuthorizationApplicator.Request('{}')
    request.job_name = "job_name"
    request.parameters = {"var_1": "val_1"}
    request.user_identity = "john.doe <john.doe@gmail.com>"
    assert request.serialize() == '{"user_identity": "john.doe horey_special_char_replacement_lessjohn.doe@gmail.comhorey_special_char_replacement_more", "job_name": "job_name", "parameters": {"var_1": "val_1"}}'


@pytest.mark.skip(reason="Can not test")
def test_authorization_job_authorize_permit():
    request = AuthorizationApplicator.Request(json.dumps({"job_name": "job_name", "parameters": {"var_1": "val_1"}, "user_identity": "user_identity"}))
    assert authorization_job.authorize(request)


@pytest.mark.skip(reason="Can not test")
def test_authorization_job_authorize_deny_var():
    request = AuthorizationApplicator.Request(json.dumps({"job_name": "job_name", "parameters": {"_": "val_1"}, "user_identity": "user_identity"}))
    assert not authorization_job.authorize(request)


@pytest.mark.skip(reason="Can not test")
def test_authorization_job_authorize_deny_val():
    request = AuthorizationApplicator.Request(json.dumps({"job_name": "job_name", "parameters": {"var_1": "_"}, "user_identity": "user_identity"}))
    assert not authorization_job.authorize(request)


@pytest.mark.skip(reason="Can not test")
def test_authorization_job_authorize_deny_identity():
    request = AuthorizationApplicator.Request(json.dumps({"job_name": "job_name", "parameters": {"var_1": "val_1"}, "user_identity": "_"}))
    assert not authorization_job.authorize(request)


@pytest.mark.skip(reason="Can not test")
def test_authorization_job_authorize_deny_job_name():
    request = AuthorizationApplicator.Request(json.dumps({"job_name": "_", "parameters": {"var_1": "val_1"}, "user_identity": "user_identity"}))
    assert not authorization_job.authorize(request)


if __name__ == "__main__":
    test_authorization_applicator_serialize()
    test_authorization_applicator_deserialize()
    test_authorization_applicator_request_serialize()
    test_authorization_applicator_request_init()
    test_authorization_job_authorize_permit()
    test_authorization_job_authorize_deny_var()
    test_authorization_job_authorize_deny_val()
    test_authorization_job_authorize_deny_identity()
    test_authorization_job_authorize_deny_job_name()
    test_authorization_applicator_request_serialize_special_chars()
    test_authorization_applicator_request_init_special_chars()
