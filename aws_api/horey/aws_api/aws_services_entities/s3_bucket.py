"""
Module handling S3 buckets
"""
import json
from aws_object import AwsObject


class S3Bucket(AwsObject):
    """
    Class representing S3 bucket.
    """
    def __init__(self, dict_src, from_cache=False):
        self.acl = None
        self.policy = None
        self.bucket_objects = []

        super().__init__(dict_src)
        if from_cache:
            self._init_bucket_from_cache(dict_src)
            return

        init_options = {
                        "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
                        "CreationDate": self.init_default_attr
                        }

        self.init_attrs(dict_src, init_options)

    def _init_bucket_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {
                   'creation_date':  self.init_date_attr_from_formatted_string,
                   'acl':  self._init_acl_from_cache,
                   'policy':  self._init_policy_from_cache,
                   }

        self._init_from_cache(dict_src, options)

    def _init_acl_from_cache(self, _, dict_src):
        """
        Init bucket ACL from previously cached dict
        :param _:
        :param dict_src:
        :return:
        """
        if dict_src is None:
            return

        if self.acl is None:
            self.acl = S3Bucket.ACL(dict_src, from_cache=True)
        else:
            raise NotImplementedError

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
            self.acl = S3Bucket.ACL(lst_src)
        else:
            raise NotImplementedError()

    def update_policy(self, str_src):
        """
        Update Policy from AWS API response str
        :param str_src:
        :return:
        """
        if self.policy is None:
            self.policy = S3Bucket.Policy(str_src)
        else:
            raise NotImplementedError()

    class ACL(AwsObject):
        """
        Class representing S3 Bucket's ACL
        """
        def __init__(self, src_data, from_cache=False):
            super(S3Bucket.ACL, self).__init__(src_data)
            self.grants = []

            if from_cache:
                if not isinstance(src_data, dict):
                    raise TypeError("Not implemented - replacement of pdb.set_trace")
                self._init_acl_from_cache(src_data)
                return

            if not isinstance(src_data, list):
                raise TypeError("Not implemented - replacement of pdb.set_trace")

            for dict_grant in src_data:
                grant = self.Grant(dict_grant)
                self.grants.append(grant)

        def _init_acl_from_cache(self, dict_src):
            """
            Init ACL from previously cached dict
            :param dict_src:
            :return:
            """
            options = {
                       'grants': self._init_grants_from_cache,
                       }

            self._init_from_cache(dict_src, options)

        def _init_grants_from_cache(self, _, lst_src):
            """
            Init grants from previously cached list
            :param _:
            :param lst_src:
            :return:
            """
            if self.grants:
                raise NotImplementedError("Can reinit yet")
            for dict_grant in lst_src:
                grant = self.Grant(dict_grant, from_cache=True)
                self.grants.append(grant)

        class Grant(AwsObject):
            """
            Class representing S3 bucket policy Grant.
            """
            def __init__(self, dict_src, from_cache=False):
                super(S3Bucket.ACL.Grant, self).__init__(dict_src)
                if from_cache:
                    self._init_grant_from_cache(dict_src)
                    return

                init_options = {
                    "Grantee": self.init_default_attr,
                    "Permission": self.init_default_attr
                }

                self.init_attrs(dict_src, init_options)

            def _init_grant_from_cache(self, dict_src):
                """
                Init grant from previously cached dict
                :param dict_src:
                :return:
                """
                options = {}

                self._init_from_cache(dict_src, options)

    class Policy(AwsObject):
        """
        Class representing S3 Bucket policy
        """
        def __init__(self, src_, from_cache=False):
            if isinstance(src_, str):
                dict_src = json.loads(src_)
            else:
                if from_cache:
                    self._init_policy_from_cache(src_)
                    return

                raise NotImplementedError("Not yet implemented")

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

    class BucketObject(AwsObject):
        """
        Class representing one saved object in S3 bucket.
        """
        def __init__(self, src_data, from_cache=False):
            self.key = None
            super(S3Bucket.BucketObject, self).__init__(src_data)

            if from_cache:
                if not isinstance(src_data, dict):
                    raise TypeError()
                self._init_bucket_object_from_cache(src_data)
                return

            if not isinstance(src_data, dict):
                raise TypeError()

            self.key = src_data["Key"]

        def _init_bucket_object_from_cache(self, dict_src):
            """
            Init object from previously cached dict.
            :param dict_src:
            :return:
            """
            options = {}
            self._init_from_cache(dict_src, options)

            self.init_date_attr_from_formatted_string("LastModified", dict_src["dict_src"]["LastModified"])
            self.size = dict_src["dict_src"]["Size"]
