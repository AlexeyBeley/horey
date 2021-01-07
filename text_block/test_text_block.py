import os
import sys
import pdb

sys.path.insert(0, os.path.abspath("../src"))
from text_block import TextBlock


def test_text_block_format_pprint():
    tb = TextBlock("Header 1")
    tb.lines.append("line 1 1")
    tb.lines.append("line 1 2")

    tb_1_1 = TextBlock("Header 1 1")
    tb_1_1.lines.append("line 1 1 1")
    tb_1_1.lines.append("line 1 1 2")
    tb.blocks.append(tb_1_1)

    tb_1_2 = TextBlock("Header 1 2")
    tb_1_2.lines.append("line 1 2 1")
    tb_1_2.lines.append("line 1 2 2")

    tb_1_2_1 = TextBlock("Header 1 2 1")
    tb_1_2_1.lines.append("line 1 2 1 1")
    tb_1_2_1.lines.append("line 1 2 1 2")

    tb_1_2.blocks.append(tb_1_2_1)
    tb.blocks.append(tb_1_2)

    tb_1_3 = TextBlock("Header 1 3")
    tb_1_3.lines.append("line 1 3 1")
    tb_1_3.lines.append("line 1 3 2")
    tb.blocks.append(tb_1_3)

    print(tb.format_pprint())


if __name__ == "__main__":
    test_text_block_format_pprint()

