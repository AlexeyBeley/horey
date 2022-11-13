"""
sudo mount -t nfs4 -o  nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport  172.31.14.49:/ /home/ubuntu/efs
"""
import pdb
import traceback
import pytest
import os
from horey.h_logger import get_logger

logger = get_logger()


# region done
@pytest.mark.skip(reason="")
def test_log_multiline():
    try:
        raise RuntimeError("test")
    except Exception as e:
        logger.exception(traceback.format_exc(8))


if __name__ == "__main__":
    test_log_multiline()
