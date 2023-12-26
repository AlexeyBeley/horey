"""
Security domain tree.

"""

from horey.h_logger import get_logger

logger = get_logger()


class SecurityDomainTree:
    """
    Node and tree.

    """

    def __init__(self, root):
        self.root = root
        self.node_ids = [root.id]
        self.managed_policy_arns = [root.id]

    def add_child(self, node_parent, node_child):
        """
        Add child if not yet seen.

        :param node_parent:
        :param node_child:
        :return:
        """

        breakpoint()

    class Node:
        def __init__(self, uid, access_type, policies):
            self.id = uid
            self.access_type = access_type
            self.policies = policies
            self.children = []


