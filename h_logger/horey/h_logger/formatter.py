import logging
import datetime

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)s: %(message)s"
)


class MultilineFormatter(logging.Formatter):
    """[2022-01-10 19:30:31,07111]"""

    def format(self, record):
        date_created = datetime.datetime.fromtimestamp(record.created)
        ret = f"[{date_created.strftime('%Y-%m-%d %H:%M:%S,%f')}] {record.levelname}:{record.filename}:{record.lineno}: {record.msg}"
        ret = ret.replace("\r", "")
        ret = ret.strip("\n")
        ret = ret.replace("\n", "\\n")
        return ret
