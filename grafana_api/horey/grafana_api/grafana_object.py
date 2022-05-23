import pdb


class GrafanaObject:
    def __init__(self):
        self.dict_src = {}

    def init_values(self, dict_src, options):
        bugs = []
        for key, value in dict_src.items():
            if key not in options:
                bugs.append(key)
                continue
            options[key](key, value)
        if bugs:
            str_error = "\n".join([f'"{key}": self.init_default,' for key in bugs])
            raise RuntimeError(str_error)

    def generate_create_request(self):
        raise NotImplementedError()

    def init_default(self, key, value):
        setattr(self, key, value)
