import pdb
import uuid


class Message:
    def __init__(self, dic_src=None):
        self._dict_src = dic_src
        self._uuid = None
        self._data = None
        self._type = None

    @property
    def uuid(self):
        return self._uuid
    
    @uuid.setter
    def uuid(self, value):
        if not isinstance(value, str):
            raise ValueError(value)
        self._uuid = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, str):
            raise ValueError(value)
        self._data = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if not isinstance(value, str):
            raise ValueError(value)
        self._type = value
    
    @property
    def dict_src(self):
        return self._dict_src

    @dict_src.setter
    def dict_src(self, value):
        self._dict_src = value

    def generate_uuid(self):
        self.uuid = str(uuid.uuid4())

    def init_from_dict(self, dict_src):
        private_attrs = [key[1:] for key in self.__dict__ if key.startswith("_")]
        for key, value in dict_src.items():
            if key not in private_attrs:
                raise ValueError(key)
            setattr(self, key, value)

    def convert_to_dict(self):
        return {key[1:]: value for key, value in self.__dict__.items() if key.startswith("_")}
