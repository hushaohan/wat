from . website import *


class NoIP(Website):

    DEFAULT_OPERATION_STATUS_STUCK_THRESHOLD = 3600 * 24 * 25  # seconds
    DEFAULT_OPERATION_ERROR_TIME_THRESHOLD = 3600 * 24 * 6  # seconds
    DEFAULT_OPERATION_ATTEMPT_PERIOD = 24  # hours
    DEFAULT_NUM_HOSTS = 3

    def __init__(self, num_hosts):
        self._num_hosts = num_hosts

    @property
    def name(self):
        return 'No-IP'

    @property
    def operation(self):
        return 'Refresh'

    def login(self, webdriver, username, password):
        webdriver.get('https://www.noip.com/login')
        webdriver.find_elements_by_css_selector('#clogs > input:nth-child(1)')[0].send_keys(username)
        webdriver.find_elements_by_css_selector('#clogs > input:nth-child(2)')[0].send_keys(password)
        webdriver.find_elements_by_css_selector('button.span12')[0].click()
        if not wait_for_any_elements(webdriver, ["//span[contains(text(), 'Dynamic DNS')]"]):
            return Status.ERROR_WITH_LOGIN
        elif not len(webdriver.find_elements_by_xpath("//span[contains(text(), 'Dynamic DNS')]")) == 1:
            return Status.UNEXPECTED_LANDING_PAGE
        else:
            webdriver.find_elements_by_xpath("//span[contains(text(), 'Dynamic DNS')]")[0].click()
            return Status.OK

    def operate(self, webdriver):
        if len(webdriver.find_elements_by_class_name('fa-cog')) == self._num_hosts:
            return Status.OPERATION_UNNECESSARY
        else:
            while True:
                elms_torefresh = webdriver.find_elements_by_class_name('fa-refresh')
                if not len(elms_torefresh) + len(webdriver.find_elements_by_class_name('fa-cog')) == self._num_hosts:
                    return Status.ERROR_WITH_OPERATION
                else:
                    elms_torefresh[0].click()
                    webdriver.implicitly_wait(WEBDRIVER_LOADING_WAIT_TIME)
                    if len(webdriver.find_elements_by_class_name('fa-cog')) == self._num_hosts:
                        return SUCCESSFUL_OPERATION
