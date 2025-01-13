"""
AWS SESV2EmailTemplate representation
"""

from horey.aws_api.aws_services_entities.aws_object import AwsObject


class SESV2EmailTemplate(AwsObject):
    """
    AWS SESV2EmailTemplate class
    """

    def __init__(self, dict_src, from_cache=False):
        self.template_content = None
        super().__init__(dict_src)

        if from_cache:
            self._init_object_from_cache(dict_src)
            return

        init_options = {
            "TemplateName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "CreatedTimestamp": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def _init_object_from_cache(self, dict_src):
        """
        Init from cache
        :param dict_src:
        :return:
        """
        options = {}
        self._init_from_cache(dict_src, options)

    def update_from_raw_response(self, dict_src):
        """
        Standard

        :param dict_src:
        :return:
        """
        init_options = {
            "TemplateName": lambda x, y: self.init_default_attr(
                x, y, formatted_name="name"
            ),
            "TemplateContent": self.init_default_attr,
        }

        self.init_attrs(dict_src, init_options)

    def generate_create_request(self):
        """
        Standard

        :return:
        """
        request = {"TemplateName": self.name, "TemplateContent": self.template_content}

        return request

    def generate_update_request(self, desired_state):
        """
        Standard

        :param desired_state:
        :return:
        """

        request = {"TemplateName": self.name, "TemplateContent": desired_state.template_content} if \
            desired_state.template_content != self.template_content else \
            None

        return request

    @property
    def arn(self):
        """
        Standard.

        :return:
        """
        return f"arn:aws:ses:{self.region.region_mark}:{self.account_id}:template/{self.name}"
