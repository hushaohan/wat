from . website import *
from .. import config
from time import sleep


class NoIP(Website):

    DEFAULT_OPERATION_STATUS_STUCK_THRESHOLD = 3600 * 24 * 20  # seconds
    DEFAULT_OPERATION_ERROR_TIME_THRESHOLD = 3600 * 24 * 2  # seconds
    DEFAULT_OPERATION_ATTEMPT_PERIOD = 3600 * 24  # seconds

    @property
    def name(self):
        return 'No-IP'

    @property
    def operation(self):
        return 'Refresh'

    def login(self, webdriver, username, password):
        webdriver.get('https://www.noip.com/login')
        webdriver.find_elements_by_css_selector(
            '#clogs > input:nth-child(1)'
        )[0].send_keys(username)
        webdriver.find_elements_by_css_selector(
            '#clogs > input:nth-child(2)'
        )[0].send_keys(password)
        webdriver.find_elements_by_css_selector('button.span12')[0].click()
        if not wait_for_any_elements(
            webdriver, ["//span[contains(text(), 'Dynamic DNS')]"]
        ):
            return Status.ERROR_WITH_LOGIN
        elif not len(webdriver.find_elements_by_xpath(
            "//span[contains(text(), 'Dynamic DNS')]"
        )) == 1:
            return Status.UNEXPECTED_LANDING_PAGE
        else:
            webdriver.find_elements_by_xpath(
                "//span[contains(text(), 'Dynamic DNS')]"
            )[0].click()
            sleep(config.WEBDRIVER_LOADING_WAIT_TIME)
            return Status.OK

    def operate(self, webdriver):
        num_elms_refreshed = 0
        while True:
            elms = webdriver.find_elements_by_class_name('btn-confirm')
            if len(elms) > 0:
                elms[0].click()
                num_elms_refreshed += 1
                wait_a_bit(webdriver)
            else:
                break
        if num_elms_refreshed > 0:
            return Status.SUCCESSFUL_OPERATION
        else:
            return Status.OPERATION_UNNECESSARY
