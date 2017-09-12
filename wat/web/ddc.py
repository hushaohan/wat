import time
from . website import *


class DDC(Website):

    DEFAULT_OPERATION_STATUS_STUCK_THRESHOLD = 1  # seconds
    DEFAULT_OPERATION_ERROR_TIME_THRESHOLD = 3  # seconds
    DEFAULT_OPERATION_ATTEMPT_PERIOD = 1  # seconds

    @property
    def name(self):
        return 'DefensiveDrivingCourse'

    @property
    def operation(self):
        return 'Auto-Advancing'

    def login(self, webdriver, username, password):
        webdriver.get((
            'https://home.uceusa.com/Courses/LoggedOut.aspx?'
            'host=newyorksafetycouncil_new'
        ))
        webdriver.find_element_by_id(
            'LoginControlObject_UsernameTextBox'
        ).send_keys(username)
        webdriver.find_element_by_id(
            'LoginControlObject_PasswordTextBox'
        ).send_keys(password)
        webdriver.find_element_by_id('LoginButton').click()
        webdriver.switch_to_frame('mainContent')
        webdriver.find_element_by_id('got_it').click()
        time.sleep(1)
        try:
            webdriver.switch_to_frame('mainContent')
        except:
            pass
        try:
            webdriver.find_element_by_id('ResumeCourse').click()
            return Status.OK
        except:
            return Status.ERROR_WITH_LOGIN

    def operate(self, webdriver):
        while True:
            try:
                time.sleep(1)
                h, m, s = [
                    int(d) for d
                    in webdriver.find_element_by_id(
                        'TimeRemainingClock'
                    ).text.split(':')]
                t = h * 3600 + m * 60 + s
                if t > 0:
                    time.sleep(h * 3600 + m * 60 + s)
                else:
                    webdriver.find_element_by_id('next_top').click()
            except:
                return Status.ERROR_WITH_OPERATION
