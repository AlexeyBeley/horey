"""
Module handling AWS route53 hosted zone
"""
from aws_object import AwsObject


class HostedZone(AwsObject):
    """
    Class representing AWS Route53 hosted zone.
    """
    def __init__(self, dict_src, from_cache=False):
        self.records = []
        super().__init__(dict_src)
        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
                        "Id": lambda x, y: self.init_default_attr(x, y, formatted_name="id"),
                        "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
                        "CallerReference": self.init_default_attr,
                        "Config": self.init_default_attr,
                        "ResourceRecordSetCount": self.init_default_attr,
                        "LinkedService": self.init_default_attr,
                        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init the object from saved cache dict
        :param dict_src:
        :return:
        """
        options = {"records": self._init_records_from_cache}
        self._init_from_cache(dict_src, options)

    def update_record_set(self, dict_src):
        """
        Update information from AWS API response
        :param dict_src:
        :return:
        """
        self.records.append(self.Record(dict_src))

    def _init_records_from_cache(self, _, lst_src):
        """
        Init records with aws api information
        :param _:
        :param lst_src:
        :return:
        """
        if self.records:
            raise NotImplementedError("Can't reinit existing")

        for record in lst_src:
            self.records.append(self.Record(record, from_cache=True))

    class Record(AwsObject):
        """
        Class representing AWS hosted zone record
        """
        def __init__(self, dict_src, from_cache=False):

            super().__init__(dict_src)
            if from_cache:
                self._init_object_from_cache(dict_src)
                return

            init_options = {
                "Name": lambda x, y: self.init_default_attr(x, y, formatted_name="name"),
                "Type": self.init_default_attr,
                "AliasTarget": self.init_default_attr,
                "TTL": self.init_default_attr,
                "ResourceRecords": self.init_default_attr,
                "SetIdentifier": self.init_default_attr,
                "Weight": self.init_default_attr,
                "MultiValueAnswer": self.init_default_attr,
                "HealthCheckId": self.init_default_attr,
            }

            self.init_attrs(dict_src, init_options)

        def _init_object_from_cache(self, dict_src):
            """
            Init the object from saved cache dict
            :param dict_src:
            :return:
            """
            options = {}
            self._init_from_cache(dict_src, options)
