from enum import Enum
import pdb

from environment_configuration_policy import EnvironmentConfigurationPolicy


class GradeConfigurationPolicy(EnvironmentConfigurationPolicy):
    def __init__(self):
        self._grade = None
        super().__init__()

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        if value not in self.GradeValue.__members__.keys():
            raise ValueError(value)

        if self._grade is not None:
            if getattr(self.GradeValue, value).value < getattr(self.GradeValue, self._grade).value:
                raise ValueError(f"Can not downgrade from {self._grade} to {value}")

        self._grade = value

    @property
    def int_grade(self):
        return getattr(self.GradeValue, self._grade).value

    class GradeValue(Enum):
        LOCAL = 0
        QA = 1
        STG = 2
        PROD = 3
