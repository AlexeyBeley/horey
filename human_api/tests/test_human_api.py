import datetime

from horey.human_api.human_api import HumanAPI
from horey.human_api.sprint import Sprint


def test_human_api(self):
    sprint = Sprint()
    sprint.start_date = datetime.datetime.now()
    sprint.end_date = sprint.start_date + datetime.timedelta(days=14)
    sprint.reduce_days(2)
    sprint.reduce_week_days("fri", "sat")


if __name__ == "__main__":
    test_human_api()
    test
