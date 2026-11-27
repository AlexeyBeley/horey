"""
Index pattern.

"""

from horey.opensearch_api.opensearch_object import OpensearchObject


class IndexPattern(OpensearchObject):
    """
    Main class.
    """
    def __init__(self, dict_src):
        self.name = None
        self.index_template = None
        super().__init__(dict_src)
