from enum import Enum


from infrastructure_configuration import InfrastructureConfiguration


class AWSConfiguration(InfrastructureConfiguration):
    def __init__(self):
        self._region_mark = None
        self._logs_bucket_name = None

    @property
    def region_human_readable_name(self):
        all_values = {
            self.RegionMark.USEAST1: "N.Virginia"
        }
        return all_values[self.region_mark]

    @region_human_readable_name.setter
    def region_human_readable_name(self, _):
        raise ValueError("Static value")

    @property
    def region_mark(self):
        if self._region_mark is None:
            raise ValueError("Accessing unset parameter")

        return self._region_mark

    @region_mark.setter
    def region_mark(self, value):
        if value not in self.RegionMark:
            raise ValueError(value)
        self._region_mark = value

    @property
    def logs_bucket_name(self):
        if self.grade > self.GradeValue.LOCAL:
            return f"logs-backup-{self.grade}"

        if self._logs_bucket_name is None:
            self._logs_bucket_name = f"logs-backup-{self.name}"

        return self._logs_bucket_name

    @logs_bucket_name.setter
    def logs_bucket_name(self, value):
        if self.grade > self.GradeValue.LOCAL:
            raise ValueError("Static value")
        else:
            self._logs_bucket_name = value

    class RegionMark(Enum):
        USEAST1 = "us-east-1"
