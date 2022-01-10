import logging
import pdb


formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)s: %(message)s")
class MultilineFormatter(logging.Formatter):
    def format(self, record):
        pdb.set_trace()
        formatted = super().format(record)
        while "\r" in record:
            record = record.replace("\r", "")
        while "\n" in record:
            record = record.replace("\n", "\\n")