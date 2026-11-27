"""
Test AWS client.

"""
import json

import pytest

from horey.aws_api.aws_clients.elasticsearch_client import ElasticsearchClient
from horey.aws_api.aws_services_entities.elasticsearch_domain import ElasticsearchDomain
from horey.aws_api.base_entities.region import Region


# pylint: disable=missing-function-docstring

@pytest.fixture(name="elasticsearch_client")
def fixture_elasticsearch_client(main_cache_dir_path):
    client = ElasticsearchClient()
    client.main_cache_dir_path = main_cache_dir_path
    return client


@pytest.fixture(name="region")
def fixture_region():
    region = Region.get_region("us-west-2")
    return region


@pytest.mark.done
def test_init_elasticsearch_client(elasticsearch_client):
    assert isinstance(elasticsearch_client, ElasticsearchClient)


@pytest.mark.done
def test_get_region_versions(elasticsearch_client, region):
    versions = elasticsearch_client.get_region_versions(region)
    assert len(versions) > 0
    assert "OpenSearch_2.15" in versions


@pytest.mark.done
def test_get_max_opensearch_version(elasticsearch_client, region):
    version = elasticsearch_client.get_max_opensearch_version(region)
    assert version


@pytest.mark.done
def test_provision_domain(elasticsearch_client, region):
    domain = ElasticsearchDomain({})
    domain.name = "test"
    domain.region = region
    domain.tags = [{"Key": "Name", "Value": domain.name}]
    domain.advanced_options = {'indices.fielddata.cache.size': '20', 'indices.query.bool.max_clause_count': '1024',
                               'override_main_response_version': 'false',
                               'rest.action.multi.allow_explicit_index': 'true'}
    domain.node_to_node_encryption_options = {'Enabled': True}
    domain.elasticsearch_cluster_config = {'InstanceType': 't3.medium.elasticsearch', 'InstanceCount': 1,
                                           'DedicatedMasterEnabled': False, 'ZoneAwarenessEnabled': False,
                                           'WarmEnabled': False, 'ColdStorageOptions': {'Enabled': False}}
    domain.ebs_options = {'EBSEnabled': True, 'VolumeType': 'gp3', 'VolumeSize': 200, 'Iops': 3000, 'Throughput': 250}
    domain.access_policies = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "es:*",
      "Resource": f"arn:aws:es:{region.region_mark}:{elasticsearch_client.account_id}:domain/{domain.name}/*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "1.1.1.1/32"
        }
      }
    }]})
    domain.cognito_options = {'Enabled': False}
    domain.encryption_at_rest_options = {'Enabled': True, 'KmsKeyId': f'arn:aws:kms:{region.region_mark}:{elasticsearch_client.account_id}:key/7eebfaf'}
    domain.elasticsearch_version = elasticsearch_client.get_max_opensearch_version(region)
    elasticsearch_client.provision_domain(domain)
    assert domain.domain_processing_status == "Active"


@pytest.mark.done
def test_wait_for_status(elasticsearch_client, region):
    domain = ElasticsearchDomain({})
    domain.name = "test"
    domain.region = region
    elasticsearch_client.wait_for_status(domain, elasticsearch_client.update_domain_information, [domain.State.ACTIVE],
                         [domain.State.CREATING,
                          domain.State.UPDATING_ENGINE_VERSION,
                          domain.State.UPDATING_SERVICE_SOFTWARE,
                          domain.State.MODIFYING],
                         [domain.State.DELETING,
                          domain.State.ISOLATED
                          ])


@pytest.mark.done
def test_dispose_domain(elasticsearch_client, region):
    domain = ElasticsearchDomain({})
    domain.name = "test"
    domain.region = region
    elasticsearch_client.dispose_domain(domain)
