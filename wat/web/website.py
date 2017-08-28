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


def wait_for_any_elements(webdriver, elms_xpaths):
    rounds = 0
    while rounds < config.MAX_WEBDRIVER_LOADING_WAIT_ROUNDS:
        webdriver.implicitly_wait(config.WEBDRIVER_LOADING_WAIT_TIME)
        for elm_xpath in elms_xpaths:
            if webdriver.find_elements_by_xpath(elm_xpath):
                return True
        rounds += 1
    return False


def wait_a_bit(webdriver):
    webdriver.implicitly_wait(config.WEBDRIVER_LOADING_WAIT_TIME)


class Website(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def operation(self):
        pass

    @abstractmethod
    def login(self, webdriver, username, password):
        pass

    @abstractmethod
    def operate(self, webdriver):
        pass
