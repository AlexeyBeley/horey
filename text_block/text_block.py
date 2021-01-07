"""
Module to handle readable text.
"""


class TextBlock:
    """
    Text block class.
    """
    def __init__(self, header):
        self.header = header
        self.lines = []
        self.blocks = []
        self.footer = []

    def __str__(self):
        ret = self.header
        ret += "\n" + "\n".join(self.lines)
        ret += "\n" + "\n".join([str(block) for block in self.blocks])
        ret += "\n" + "\n".join(self.footer)
        return ret

    def format_pprint(self, shift=0):
        """
        Format self in a readable format.

        :param shift:
        :return:
        """
        header_shift = " "*shift
        ret = f"{header_shift}* {self.header}"

        if len(self.lines) > 0:
            line_shift = " "*(shift+2)
            ret += f"\n{line_shift}" + f"\n{line_shift}".join(self.lines)

        if len(self.blocks) > 0:
            ret += "\n" + "\n".join([block.format_pprint(shift+2) for block in self.blocks])

        if len(self.footer) > 0:
            ret += "\n" + "\n".join(self.footer)
        return ret
