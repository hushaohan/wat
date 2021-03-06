from . website import *
from .. import config
from time import sleep


class XiaMi(Website):

    DEFAULT_OPERATION_STATUS_STUCK_THRESHOLD = 3600 * (24 + 6)  # seconds
    DEFAULT_OPERATION_ERROR_TIME_THRESHOLD = 3600 * 12  # seconds
    DEFAULT_OPERATION_ATTEMPT_PERIOD = 3600 * 3  # seconds

    @property
    def name(self):
        return 'XiaMi'

    @property
    def operation(self):
        return 'Check-In'

    def login(self, webdriver, username, password):
        rounds, switches = 0, None
        while rounds < config.MAX_WEBDRIVER_LOADING_WAIT_ROUNDS:
            webdriver.get('https://login.xiami.com/member/login')
            switches = webdriver.find_elements_by_id("J_LoginSwitch")
            if not switches:
                rounds += 1
                sleep(config.WEBDRIVER_LOADING_WAIT_TIME)
            else:
                switches[0].click()
                break
        if not switches:
            return Status.ERROR_WITH_LOGIN
        webdriver.find_element_by_id('account').send_keys(username)
        webdriver.find_element_by_id('pw').send_keys(password)
        webdriver.find_element_by_id('submit').click()
        if not wait_for_any_elements(
            webdriver,
            ["//b[@class='icon tosign done']", "//b[@class='icon tosign']"]
        ):
            return Status.ERROR_WITH_LOGIN
        else:
            return Status.OK

    def operate(self, webdriver):
        if webdriver.find_elements_by_xpath("//b[@class='icon tosign done']"):
            return Status.OPERATION_UNNECESSARY
        else:
            elms_tosign = webdriver.find_elements_by_xpath(
                "//b[@class='icon tosign']"
            )
            if len(elms_tosign) > 0:
                elms_tosign[0].click()
                if wait_for_any_elements(
                    webdriver, ["//b[@class='icon tosign done']"]
                ):
                    return Status.SUCCESSFUL_OPERATION
                else:
                    return Status.ERROR_WITH_OPERATION
