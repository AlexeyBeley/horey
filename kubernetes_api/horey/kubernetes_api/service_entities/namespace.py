from horey.kubernetes_api.service_entities.kubernetes_object import KubernetesObject


class Namespace(KubernetesObject):
    def __init__(self, obj_src, from_cache=False):
        super().__init__(obj_src)

        if from_cache:
            raise NotImplementedError()

        init_options = {
            "api_version": self.init_default_attr,
            "kind": self.init_default_attr,
            "metadata": self.init_default_attr,
            "spec": self.init_default_attr,
            "status": self.init_default_attr,
        }
        self.init_attrs(obj_src.to_dict(), init_options)

