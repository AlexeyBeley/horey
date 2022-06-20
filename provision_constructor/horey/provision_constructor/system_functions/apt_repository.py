import pdb
from horey.h_logger import get_logger

logger = get_logger()


class APTRepository:
    def __init__(self):
        self.name = None
        self.str_src = None

    def init_from_line(self, str_src):
        self.str_src = str_src
        pdb.set_trace()
