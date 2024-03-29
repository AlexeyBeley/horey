"""
Security domain tree.

"""

from horey.h_logger import get_logger
from horey.common_utils.text_block import TextBlock
from horey.common_utils.common_utils import CommonUtils

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

    def convert_to_dict(self):
        """
        Serialize.

        :return:
        """

        return CommonUtils.convert_to_dict(self.__dict__)

    def generate_security_domain_graph(self):
        """
        Generate graph.

        :return:
        """

        nodes, edges = self.root.generate_security_domain_graph_nodes_and_edges()
        return {"nodes": nodes, "edges": edges}


    class Node:
        """
        Security tree node.

        """

        def __init__(self, uid, access_type, policies):
            self.id = uid
            self.full_admin = False
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

        def convert_to_dict(self):
            """
            Serialize.

            :return:
            """

            return CommonUtils.convert_to_dict(self.__dict__)

        def generate_security_domain_graph_nodes_and_edges(self):
            """
            Nodes and edges drawable in UI.

            :return:
            """

            nodes, edges = [], []
            nodes.append({"id": self.id, "label": self.id.split(":")[-1]})

            for child in self.children:
                child_nodes, child_edges = child.generate_security_domain_graph_nodes_and_edges()
                edges.append({"source": self.id, "target": child.id, "label": child.access_type})
                edges += child_edges
                nodes += child_nodes

            return nodes, edges
