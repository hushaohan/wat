#! /usr/bin/env python2.7

import os
import smtplib
import getpass
import sys
import keyring
from datetime import datetime
from time import time, sleep
from selenium import webdriver as wd
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from enum import Enum
from config import *


class Status(Enum):
    ERROR_WITH_CHECK_IN = -1
    SUCCESSFULLY_CHECKED_IN = 0
    ALREADY_CHECKED_IN = 1


def send_email(me, you, msg_content):
    msg = MIMEText(msg_content)
    msg['Subject'] = msg_content
    msg['From'] = me
    msg['To'] = you
    print 'mail'
    sender = smtplib.SMTP('localhost')
    sender.sendmail(me, [you], msg.as_string())
    sender.quit()


def login_xiami_and_attempt_check_in(email, password):
    profile = wd.FirefoxProfile()
    # profile.add_extension(extension='unblock-youku.xpi')
    # profile.set_preference('network.proxy.type', 2)
    FIREFOX_BINARY_PATH = None
    if sys.platform.find('darwin') == 0:
        FIREFOX_BINARY_PATH = FIREFOX_BINARY_PATH_OSX
    elif sys.platform.find('linux') == 0:
        FIREFOX_BINARY_PATH = FIREFOX_BINARY_PATH_LINUX
    else:
        print 'Firefox not found, exiting...'
        exit(-1)
    ff = wd.Firefox(profile, firefox_binary=FirefoxBinary(FIREFOX_BINARY_PATH))
    ff.get('https://login.xiami.com/member/login')
    ff.find_elements_by_id("J_LoginSwitch")[0].click()
    ff.find_element_by_id('account').send_keys(email)
    ff.find_element_by_id('pw').send_keys(password)
    ff.find_element_by_id('submit').click()
    try:
        while ff.current_url.find('login') >= 0:
            ff.implicitly_wait(3)
    except Exception:
        print 'timed out trying to open login page'
        pass
    ff.implicitly_wait(3)
    elms = ff.find_elements_by_xpath("//b[@class='icon tosign done']")
    if len(elms) > 0:
        status = Status.ALREADY_CHECKED_IN
    else:
        elms = ff.find_elements_by_xpath("//b[@class='icon tosign']")
        if len(elms) > 0:
            elms[0].click()
            ff.implicitly_wait(3)
            elms = ff.find_elements_by_xpath("//b[@class='icon tosign done']")
            if len(elms) > 0:
                status = Status.SUCCESSFULLY_CHECKED_IN
            else:
                status = Status.ERROR_WITH_CHECK_IN
        else:
            status = Status.ERROR_WITH_CHECK_IN
    ff.close()
    return status


def check_in_periodically(email, password):
    if not os.path.exists(last_check_in_file):
        last_check_in_time = time()
    else:
        last_check_in_time = float(open(last_check_in_file).readlines()[0].strip())
    unexpected_error_count = 0
    while True:
        try:
            if not SHOW_GUI:
                from pyvirtualdisplay import Display
                display = Display(visible=0, size=(800, 600))
                display.start()
            status = login_xiami_and_attempt_check_in(email, password)
            if not SHOW_GUI:
                display.stop()
            current_time = time()
            print current_time, datetime.fromtimestamp(current_time).strftime('%Y-%m-%d_%H:%M:%S'),
            if status == Status.SUCCESSFULLY_CHECKED_IN:
                last_check_in_time = current_time
                open(last_check_in_file, 'w').write(str(last_check_in_time) + '\n' + datetime.fromtimestamp(last_check_in_time).strftime('%Y-%m-%d_%H:%M:%S'))
                print 'SUCCESSFULLY_CHECKED_IN'
            elif status == Status.ALREADY_CHECKED_IN:
                print 'ALREADY_CHECKED_IN'
                if current_time - last_check_in_time >= 3600 * check_in_status_stuck_threshold:
                    send_email(email, email, 'Xiami check in status stuck for the past %d hours' % check_in_status_stuck_threshold)
            else:
                print 'ERROR_WITH_CHECK_IN'
                if current_time - last_check_in_time >= 3600 * check_in_error_time_threshold:
                    send_email(email, email, 'Xiami check in problems for the past %d hours' % check_in_error_time_threshold)
        except:
            print 'UNEXPECTED_ERROR_WITH_CHECK_IN', sys.exc_info()
            unexpected_error_count += 1
            if unexpected_error_count >= UNEXPECTED_ERROR_COUNT_THRESHOLD:
                send_email(email, email, 'Xiami check in unexpected error!\n' + str(sys.exc_info()))
        sleep(attempt_check_in_period)


def prompt_user_for_account_info():
    from Tkinter import Tk, Label, Entry, mainloop

    def get_account_info(evt):
        global email, password
        email = user_entry.get()
        password = pass_entry.get()
        root.destroy()

    root = Tk()
    root.wm_title('Xiami Account Info')
    Label(root, text="Username").grid(row=0)
    Label(root, text="Password").grid(row=1)

    user_entry = Entry(root)
    pass_entry = Entry(root, show='*')
    pass_entry.bind('<Return>', get_account_info)
    user_entry.grid(row=0, column=1)
    pass_entry.grid(row=1, column=1)

    if email == None:
        user_entry.focus_set()
    else:
        user_entry.insert(0, email)
        pass_entry.focus_set()
    mainloop()


if __name__ == '__main__':
    email = None
    password = None
    if len(sys.argv) > 1:
        email = sys.argv[1].lower()
    if len(sys.argv) > 2:
        password = sys.argv[2]

    if email == None:
        print 'Prompting user for account email and password!'
        prompt_user_for_account_info()
        keyring.set_password(KEYRING_SERVICE, email, password)
    else:
        if password == None:
            password = keyring.get_password(KEYRING_SERVICE, email)
            if password == None:
                print 'Prompting user %s for password!' % email
                prompt_user_for_account_info()
                keyring.set_password(KEYRING_SERVICE, email, password)
            else:
                print 'Password for ' + email + ' retrieved from keyring!'
                pass
        else:
            print 'Warning: Plaintext password on command-line not recommended!'
            pass
    check_in_periodically(email, password)
