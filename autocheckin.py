#! /usr/bin/env python2.7

import os, sys
from time import time, sleep
from selenium import webdriver as wd
import smtplib
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By


SUCCESSFULLY_CHECKED_IN = 0
ALREADY_CHECKED_IN = 1
ERROR_WITH_CHECK_IN = -1

last_check_in_file = 'last.txt'
attempt_check_in_period = 3600 * 3          # seconds
check_in_status_stuck_threshold = 24 + 1    # hours
check_in_error_time_threshold = 12          # hours

def send_email(msg_content):
    msg = MIMEText(msg_content)
    me = 'hushaohan@gmail.com'
    you = 'hushaohan@gmail.com'
    msg['Subject'] = msg_content
    msg['From'] = me
    msg['To'] = you
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()


def open_and_login_xiami_in_firefox(email, password):
    profile = wd.FirefoxProfile()
    profile.add_extension(extension='unblock-youku.xpi')
    profile.set_preference('network.proxy.type', 2); 
    ff = wd.Firefox(profile)
    ff.get('https://login.xiami.com/member/login')
    ff.find_element_by_id('email').send_keys(email)
    ff.find_element_by_id('password').send_keys(password + '\n')
    try:
        while ff.current_url.find('login') >= 0:
            ff.implicitly_wait(3)
    except Exception:
        print 'time out'
        pass
    return ff


def attempt_check_in(ff):
    elms = ff.find_elements_by_xpath("//b[@class='icon tosign done']")
    if len(elms) > 0:
        return ALREADY_CHECKED_IN
    else:
        elms = ff.find_elements_by_xpath("//b[@class='icon tosign']")
        if len(elms) > 0:
            elms[0].click()
            ff.implicitly_wait(3)
            elms = ff.find_elements_by_xpath("//b[@class='icon tosign done']")
            if len(elms) > 0:
                return SUCCESSFULLY_CHECKED_IN
            else:
                return ERROR_WITH_CHECK_IN
        else:
            return ERROR_WITH_CHECK_IN
            

def check_in_periodically():
    if not os.path.exists(last_check_in_file):
        last_check_in_time = time()
    else:
        last_check_in_time = float(open(last_check_in_file).read().strip())
    while True:
        ff = open_and_login_xiami_in_firefox(email, password)
        ret = attempt_check_in(ff)
        current_time = time()
        print current_time, 
        if ret == SUCCESSFULLY_CHECKED_IN:
            last_check_in_time = current_time
            open(last_check_in_file, 'w').write(str(last_check_in_time))
            print 'SUCCESSFULLY_CHECKED_IN'
        elif ret == ALREADY_CHECKED_IN:
            print 'ALREADY_CHECKED_IN'
            if current_time - last_check_in_time >= 3600 * check_in_status_stuck_threshold:
                sendmail('Xiami check in status stuck for the past %d hours' % check_in_status_stuck_threshold)
        else:
            print 'ERROR_WITH_CHECK_IN'
            if current_time - last_check_in_time >= 3600 * check_in_error_time_threshold:
                sendmail('Xiami check in problems for the past %d hours' % check_in_error_time_threshold)
        ff.close()
        sleep(attempt_check_in_period)


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        print 'Xiami account email and password required!'
        exit(1)
    else:
        email = sys.argv[1]
        password = sys.argv[2]
    check_in_periodically()
    