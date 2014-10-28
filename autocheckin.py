#! /usr/bin/env python2.7

import os, smtplib, getpass
from datetime import datetime
from time import time, sleep
from selenium import webdriver as wd
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display

SUCCESSFULLY_CHECKED_IN = 0
ALREADY_CHECKED_IN = 1
ERROR_WITH_CHECK_IN = -1

last_check_in_file = 'last.txt'
attempt_check_in_period = 3600 * 3          # seconds
check_in_status_stuck_threshold = 24 + 1    # hours
check_in_error_time_threshold = 12          # hours


def send_email(me, you, msg_content):
    msg = MIMEText(msg_content)
    msg['Subject'] = msg_content
    msg['From'] = me
    msg['To'] = you
    sender = smtplib.SMTP('localhost')
    sender.sendmail(me, [you], msg.as_string())
    sender.quit()


def login_xiami_and_attempt_check_in(email, password):
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

    elms = ff.find_elements_by_xpath("//b[@class='icon tosign done']")
    if len(elms) > 0:
        status = ALREADY_CHECKED_IN
    else:
        elms = ff.find_elements_by_xpath("//b[@class='icon tosign']")
        if len(elms) > 0:
            elms[0].click()
            ff.implicitly_wait(3)
            elms = ff.find_elements_by_xpath("//b[@class='icon tosign done']")
            if len(elms) > 0:
                status = SUCCESSFULLY_CHECKED_IN
            else:
                status = ERROR_WITH_CHECK_IN
        else:
            status = ERROR_WITH_CHECK_IN
    ff.close()
    return status


def check_in_periodically(email, password):
    if not os.path.exists(last_check_in_file):
        last_check_in_time = time()
    else:
        last_check_in_time = float(open(last_check_in_file).readlines()[0].strip())
    while True:
        display = Display(visible=0, size=(800, 600))
        display.start()
        status = login_xiami_and_attempt_check_in(email, password)
        display.stop()
        current_time = time()
        print current_time, datetime.fromtimestamp(current_time).strftime('%Y-%m-%d_%H:%M:%S'), 
        if status == SUCCESSFULLY_CHECKED_IN:
            last_check_in_time = current_time
            open(last_check_in_file, 'w').write(str(last_check_in_time) + '\n' + datetime.fromtimestamp(last_check_in_time).strftime('%Y-%m-%d_%H:%M:%S'))
            print 'SUCCESSFULLY_CHECKED_IN'
        elif status == ALREADY_CHECKED_IN:
            print 'ALREADY_CHECKED_IN'
            if current_time - last_check_in_time >= 3600 * check_in_status_stuck_threshold:
                send_email(email, email, 'Xiami check in status stuck for the past %d hours' % check_in_status_stuck_threshold)
        else:
            print 'ERROR_WITH_CHECK_IN'
            if current_time - last_check_in_time >= 3600 * check_in_error_time_threshold:
                send_email(email, email, 'Xiami check in problems for the past %d hours' % check_in_error_time_threshold)
        sleep(attempt_check_in_period)


if __name__ == '__main__':
    email = raw_input('User:').lower()
    password = getpass.getpass('Pass:')
    check_in_periodically(email, password)
