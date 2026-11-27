from horey.kubernetes_api.service_entities.kubernetes_object import KubernetesObject


class Pod(KubernetesObject):
    def __init__(self, obj_src=None, dict_src=None):
        super().__init__(obj_src=obj_src, dict_src=dict_src)

