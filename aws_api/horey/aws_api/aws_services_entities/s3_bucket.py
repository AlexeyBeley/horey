"""
Module handling S3 buckets
"""
import json
from horey.aws_api.aws_services_entities.aws_object import AwsObject
from horey.aws_api.base_entities.region import Region


class S3Bucket(AwsObject):
    """
    Class representing S3 bucket.
    """

    def __init__(self, dict_src, from_cache=False):
        self.acl = None
        self.policy = None
        self.bucket_objects = []
        self.index_document = None
        self.error_document = None
        self.redirect_all_requests_to = None
        self.location = None

        super().__init__(dict_src)
        if from_cache:
            self._init_bucket_from_cache(dict_src)
            return

        init_options = {
            "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "CreationDate": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def update_from_raw_response(self, dict_src):
        """
        Update from dict received from AWS API.

        :param dict_src:
        :return:
        """

        init_options = {
            "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
            "CreationDate": self.init_default_attr,
            "BucketRegion": lambda x, y: self.init_default_attr(x, y, formatted_name="location"),
            "AccessPointAlias": self.init_default_attr
        }

        return self.init_attrs(dict_src, init_options)

    def _init_bucket_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {
            "policy": self._init_policy_from_cache,
        }

        self._init_from_cache(dict_src, options)

    def _init_policy_from_cache(self, _, dict_src):
        """
        Init policy object from previously cached dict
        :param _:
        :param dict_src:
        :return:
        """
        if self.policy is not None:
            raise NotImplementedError

        if dict_src is not None:
            self.policy = S3Bucket.Policy(dict_src, from_cache=True)

    def update_objects(self, lst_src, from_cache=False):
        """
        Update objects list with new object
        :param lst_src:
        :param from_cache:
        :return:
        """
        for dict_object in lst_src:
            bucket_object = S3Bucket.BucketObject(dict_object, from_cache=from_cache)
            self.bucket_objects.append(bucket_object)

    def update_acl(self, lst_src):
        """
        Update ACL from AWS API response list
        :param lst_src:
        :return:
        """
        if self.acl is None:
            self.acl = lst_src
        elif self.acl != lst_src:
            raise NotImplementedError(f"{self.name} {self.acl=} {lst_src=}")

    def update_policy(self, str_src):
        """
        Update Policy from AWS API response str
        :param str_src:
        :return:
        """
        if self.policy is None:
            self.policy = S3Bucket.Policy(str_src)
        else:
            raise NotImplementedError(f"Policy already set: {self.policy}")

    def update_website(self, dict_src):
        """
        Update website config.

        :param dict_src:
        :return:
        """

        init_options = {
            "IndexDocument": self.init_default_attr,
            "ErrorDocument": self.init_default_attr,
            "RedirectAllRequestsTo": self.init_default_attr,
            "ResponseMetadata": lambda x, y: 0,
        }

        self.init_attrs(dict_src, init_options)

    def update_location(self, lst_src):
        """
        For more info about this ugly stuff check get_dns_records docstring
        """
        if len(lst_src) > 1:
            raise ValueError(lst_src)
        self.location = lst_src[0] if lst_src[0] is not None else "us-east-1"

    def get_dns_records(self):
        """
        If while reading this you say "WHAT????", read here and cry:
        https://docs.aws.amazon.com/general/latest/gr/s3.html#s3_website_region_endpoints
        and this:

        "
        LocationConstraint (string) --
        Specifies the Region where the bucket resides. For a list of all the Amazon S3 supported location constraints by Region, see Regions and Endpoints . Buckets in Region us-east-1 have a LocationConstraint of null .
        "

        Get all self dns records.
        :return:
        """

        mappings = {
            "us-east-2": ".",
            "us-east-1": "-",
            "us-west-1": "-",
            "us-west-2": "-",
            "af-south-1": ".",
            "ap-east-1": ".",
            "ap-south-1": ".",
            "ap-northeast-3": ".",
            "ap-northeast-2": ".",
            "ap-southeast-1": "-",
            "ap-southeast-2": "-",
            "ap-northeast-1": "-",
            "eu-west-1": "-",
            "sa-east-1": "-",
            "us-gov-west-1": "-",
            "ca-central-1": ".",
            "cn-northwest-1": ".",
            "eu-central-1": ".",
            "eu-west-2": ".",
            "eu-south-1": ".",
            "eu-west-3": ".",
            "eu-north-1": ".",
            "me-south-1": ".",
            "us-gov-east-1": ".",
        }

        if (
                self.index_document is None
                and self.error_document is None
                and self.redirect_all_requests_to is None
        ):
            return []

        return [
            f"{self.name}.s3-website{mappings[self.location]}{self.location}.amazonaws.com"
        ]

    def generate_create_request(self):
        """
        ACL='private'|'public-read'|'public-read-write'|'authenticated-read',
        'LocationConstraint': 'af-south-1'|'ap-east-1'|'ap-northeast-1'|'ap-northeast-2'|'ap-northeast-3'|'ap-south-1'|
        'ap-southeast-1'|'ap-southeast-2'|'ca-central-1'|'cn-north-1'|'cn-northwest-1'|'EU'|'eu-central-1'|'eu-north-1'|
        'eu-south-1'|'eu-west-1'|'eu-west-2'|'eu-west-3'|'me-south-1'|'sa-east-1'|'us-east-2'|'us-gov-east-1'|'us-gov-west-1'|
        'us-west-1'|'us-west-2'
        }
        """

        request = {"ACL": self.acl, "Bucket": self.name}

        # AWS bug:
        # https://stackoverflow.com/questions/51912072/invalidlocationconstraint-error-while-creating-s3-bucket-when-the-used-command-i
        if self.region.region_mark != "us-east-1":
            request["CreateBucketConfiguration"] = {
                "LocationConstraint": self.region.region_mark
            }

        return request

    def generate_put_bucket_policy_request(self):
        """
        Standard

        :return:
        """
        request = {"Policy": self.policy.generate_put_string(), "Bucket": self.name}

        return request

    def generate_put_bucket_acl_request(self):
        """
        Standard

        :return:
        """
        request = {"ACL": self.acl, "Bucket": self.name}

        return request

    def upsert_statements(self, statements):
        """
        Insert statements if not exist.

        :param statements:
        :return:
        """

        if self.policy is None:
            self.policy = self.Policy({"Version": "2012-10-17", "Statement": statements})
            return True

        for statement in statements:
            for policy_statement in self.policy.statement:
                if statement == policy_statement:
                    break
            else:
                raise NotImplementedError(f"Implement {statement}")

        return False

    @property
    def region(self):
        if self._region is None:
            if self.location is None:
                raise RuntimeError("Region and location were not set")
            self._region = Region.get_region(self.location)
        return self._region

    @region.setter
    def region(self, value):
        if not isinstance(value, Region):
            raise ValueError(value)

        self._region = value

    class Policy(AwsObject):
        """
        Class representing S3 Bucket policy
        """

        def __init__(self, src_, from_cache=False):
            self.version = None
            self.statement = []

            if isinstance(src_, str):
                dict_src = json.loads(src_)
            else:
                if from_cache:
                    self._init_policy_from_cache(src_)
                    return
                if not isinstance(src_, dict):
                    raise NotImplementedError("Not yet implemented")

                dict_src = src_

            super(S3Bucket.Policy, self).__init__(dict_src)
            if from_cache:
                raise NotImplementedError("Not yet implemented")

            init_options = {
                "Version": self.init_default_attr,
                "Statement": self.init_default_attr,
                "Id": self.init_default_attr,
            }

            self.init_attrs(dict_src, init_options)

        def _init_policy_from_cache(self, dict_src):
            """
            Init policy from previously cached dict
            :param dict_src:
            :return:
            """
            options = {}
            try:
                self._init_from_cache(dict_src, options)
            except Exception:
                print(dict_src)
                raise

        def generate_put_string(self):
            """
            Standard

            :return:
            """
            request_dict = {"Version": self.version, "Statement": self.statement}
            return json.dumps(request_dict)

        def upsert_statements(self, statements):
            """
            Insert statements if not exist.

            :param statements:
            :return:
            """

            for statement in statements:
                raise NotImplementedError(f"Implement {statement}")

            return False

    class BucketObject(AwsObject):
        """
        Class representing one saved object in S3 bucket.
        """

        def __init__(self, src_data, from_cache=False):
            self.key = None
            self.last_modified = None

            super(S3Bucket.BucketObject, self).__init__(src_data)

            if from_cache:
                self._init_bucket_object_from_cache(src_data)
                return

            init_options = {
                "Key": self.init_default_attr,
                "LastModified": self.init_default_attr,
                "ETag": self.init_default_attr,
                "Size": self.init_default_attr,
                "StorageClass": self.init_default_attr,
            }
            self.init_attrs(src_data, init_options)

        def _init_bucket_object_from_cache(self, dict_src):
            """
            Init object from previously cached dict.
            :param dict_src:
            :return:
            """
            options = {}
            self._init_from_cache(dict_src, options)

            self.size = dict_src["dict_src"]["Size"]
