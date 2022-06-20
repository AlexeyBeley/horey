import pdb
from horey.h_logger import get_logger

logger = get_logger()


class APTRepository:
    def __init__(self):
        self.name = None
        self.str_src = None
        self.file_path = None

    def init_from_line(self, str_src, file_path):
        self.str_src = str_src
        self.file_path = file_path
