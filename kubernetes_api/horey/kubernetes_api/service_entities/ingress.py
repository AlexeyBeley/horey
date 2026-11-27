from horey.kubernetes_api.service_entities.kubernetes_object import KubernetesObject


class Ingress(KubernetesObject):
    def __init__(self, obj_src=None, dict_src=None):
        super().__init__(obj_src=obj_src, dict_src=dict_src)

    def generate_provision_request(self):
        """
        Remove all the irrelevant data.

        :return:
        """

        clean_response = self.convert_to_dict()
        del clean_response["metadata"]["creation_timestamp"]
        del clean_response["metadata"]["resource_version"]
        for field in clean_response["metadata"]["managed_fields"]:
            del field["time"]
        return clean_response

