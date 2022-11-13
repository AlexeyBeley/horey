"""
Timeoff Request object
"""
import datetime
from horey.bob_api.bob_object import BobObject


class TimeoffRequest(BobObject):
    """
    Main class
    """

    def __init__(self, dict_src):
        self.employee_display_name = None
        self.end_date = None
        self.start_date = None
        self.date = None

        self._date_start = None
        self._date_end = None

        super().__init__(dict_src)

    @property
    def date_start(self):
        """
        Date starting vacation

        @return:
        """
        if self._date_start is None:
            start_date = self.start_date or self.date
            self._date_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        return self._date_start

    @property
    def date_end(self):
        """
        Date ending vacation

        @return:
        """
        if self._date_end is None:
            end_date = self.end_date or self.date
            self._date_end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        return self._date_end

    def generate_current_vacation_string(self):
        """
        User friendly message.

        @return:
        """

        return f"{self.employee_display_name}: is on vacation until [{self.date_end.strftime('%A - %d.%m')}]"
