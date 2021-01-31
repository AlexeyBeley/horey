from enum import Enum

from environment_configuration_policy import EnvironmentConfiguration


class GradeConfiguration(EnvironmentConfiguration):
    def __init__(self):
        self._grade = None
        super().__init__()

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        if value not in self.GradeValue.__members__:
            raise ValueError(value)

        if self._grade is not None:
            if value < self._grade:
                raise ValueError("Can not downgrade")

        self._grade = value

    class GradeValue(Enum):
        LOCAL = 0
        QA = 1
        STG = 2
        PROD = 3

