from abc import ABC, abstractmethod
from enum import Enum, auto
from .. import config


class Status(Enum):
    UNEXPECTED_ERROR = auto()
    ERROR_WITH_OPERATION = auto()
    ERROR_WITH_LOGIN = auto()
    PROBLEM_ACCESSING_LOGIN = auto()
    UNEXPECTED_LANDING_PAGE = auto()
    SUCCESSFUL_OPERATION = auto()
    OPERATION_UNNECESSARY = auto()
    OK = auto()


def wait_for_any_elements(webdriver, elms):
    rounds = 0
    while rounds < config.MAX_WEBDRIVER_LOADING_WAIT_ROUNDS:
        webdriver.implicitly_wait(config.WEBDRIVER_LOADING_WAIT_TIME)
        for elm in elms:
            if webdriver.find_elements_by_xpath(elm):
                return True
        rounds += 1
    return False


class Website(ABC):
    @property
    def operation_status_stuck_threshold(self):
        return self._operation_status_stuck_threshold

    @property
    def operation_error_time_threshold(self):
        return self._operation_error_time_threshold

    @property
    def operation_attempt_period(self):
        return self._operation_attempt_period

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def operation(self):
        pass

    @abstractmethod
    def login(self, webdriver, email, password):
        pass

    @abstractmethod
    def operate(self, webdriver):
        pass
