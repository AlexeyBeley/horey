"""
Security domain tree.

"""

from horey.h_logger import get_logger
from horey.common_utils.text_block import TextBlock

logger = get_logger()


class SecurityDomainTree:
    """
    Node and tree.

    """

    def __init__(self, root, aggressive=True):
        self.root = root
        self.node_ids = [root.id]
        self.managed_policy_arns = [root.id]
        self.aggressive = aggressive

    def add_child(self, node_parent, node_child):
        """
        Add child if not yet seen.

        :param node_parent:
        :param node_child:
        :return:
        """

        if node_child.id in self.node_ids:
            raise RuntimeError(f"{node_child.id} already in the tree")

        self.node_ids.append(node_child.id)
        for policy in node_child.policies:
            if not policy.arn or policy.arn in self.managed_policy_arns:
                continue
            self.managed_policy_arns.append(policy.arn)

        node_parent.children.append(node_child)

    def print(self):
        """
        Print recursive text block.

        :return:
        """

        print(self.root.generate_text_block().format_pprint())

    class Node:
        """
        Security tree node.

        """

        def __init__(self, uid, access_type, policies):
            self.id = uid
            self.access_type = access_type
            self.policies = policies
            self.children = []

        def generate_text_block(self):
            """
            Generate recursive.

            :return:
            """

            tb_ret = TextBlock(self.access_type)
            tb_ret.lines = [f"{len(self.policies)=}",
                            f"{len(self.children)=}"]
            for child in self.children:
                tb_ret.blocks.append(child.generate_text_block())

            return tb_ret
