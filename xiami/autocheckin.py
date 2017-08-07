import click
import os
import smtplib
import getpass
import sys
import keyring
from datetime import datetime
from time import time, sleep
from selenium import webdriver
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
from enum import Enum
from . config import *


class Status(Enum):
    ERROR_WITH_CHECK_IN = -1
    SUCCESSFULLY_CHECKED_IN = 0
    ALREADY_CHECKED_IN = 1


def send_email(me, you, msg_content):
    msg = MIMEText(msg_content)
    msg['Subject'] = msg_content
    msg['From'] = me
    msg['To'] = you
    print('mail')
    sender = smtplib.SMTP('localhost')
    sender.sendmail(me, [you], msg.as_string())
    sender.quit()


def login_xiami_and_attempt_check_in(wd, email, password):
    wd.get(XIAMI_LOGIN_URL)
    wd.find_elements_by_id("J_LoginSwitch")[0].click()
    wd.find_element_by_id('account').send_keys(email)
    wd.find_element_by_id('pw').send_keys(password)
    wd.find_element_by_id('submit').click()

    try:
        while not wd.find_elements_by_xpath("//b[@class='icon tosign done']") and not wd.find_elements_by_xpath("//b[@class='icon tosign']"):
            wd.implicitly_wait(3)
    except Exception:
        print('timed out trying to log in')
        pass

    elms = wd.find_elements_by_xpath("//b[@class='icon tosign done']")
    if len(elms) > 0:
        status = Status.ALREADY_CHECKED_IN
    else:
        elms = wd.find_elements_by_xpath("//b[@class='icon tosign']")
        if len(elms) > 0:
            elms[0].click()
            wd.implicitly_wait(3)
            elms = wd.find_elements_by_xpath("//b[@class='icon tosign done']")
            if len(elms) > 0:
                status = Status.SUCCESSFULLY_CHECKED_IN
            else:
                status = Status.ERROR_WITH_CHECK_IN
        else:
            status = Status.ERROR_WITH_CHECK_IN
    wd.close()
    return status


def check_in_periodically(email, password, headless):
    if not os.path.exists(last_check_in_file):
        last_check_in_time = time()
    else:
        last_check_in_time = float(open(last_check_in_file).readlines()[0].strip())
    unexpected_error_count = 0
    while True:
        try:
            wd = webdriver.PhantomJS() if headless else webdriver.Firefox()
            status = login_xiami_and_attempt_check_in(wd, email, password)
            current_time = time()
            print('{} {}'.format(current_time, datetime.fromtimestamp(current_time).strftime('%Y-%m-%d_%H:%M:%S')), end=' ')
            if status == Status.SUCCESSFULLY_CHECKED_IN:
                last_check_in_time = current_time
                open(last_check_in_file, 'w').write(str(last_check_in_time) + '\n' + datetime.fromtimestamp(last_check_in_time).strftime('%Y-%m-%d_%H:%M:%S'))
                print('SUCCESSFULLY_CHECKED_IN')
            elif status == Status.ALREADY_CHECKED_IN:
                print('ALREADY_CHECKED_IN')
                if current_time - last_check_in_time >= 3600 * check_in_status_stuck_threshold:
                    send_email(email, email, 'Xiami check in status stuck for the past %d hours' % check_in_status_stuck_threshold)
            else:
                print('ERROR_WITH_CHECK_IN')
                if current_time - last_check_in_time >= 3600 * check_in_error_time_threshold:
                    send_email(email, email, 'Xiami check in problems for the past %d hours' % check_in_error_time_threshold)
        except:
            print('UNEXPECTED_ERROR_WITH_CHECK_IN {}'.format(sys.exc_info()))
            unexpected_error_count += 1
            if unexpected_error_count >= UNEXPECTED_ERROR_COUNT_THRESHOLD:
                send_email(email, email, 'Xiami check in unexpected error!\n' + str(sys.exc_info()))
        sleep(attempt_check_in_period)


def prompt_user_for_account_info(email):
    import tkinter
    import tkinter.simpledialog
    tkinter.Tk().withdraw()
    return tkinter.simpledialog.askstring('Password', 'Xiami password for {}:'.format(email), show='*')


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--email', '-e', type=str, default='hushaohan@gmail.com',
              help='Xiami account email address')
@click.option('--password-now/--no-password-now', default=True,
              help='If now, prompt user on cmd-line for password now (thus, should not be run in background); otherwise, open a gui password prompt that can be filled later.')
@click.option('--headless/--no-headless', default=True,
              help='Indicate whether or not headless mode should be used.')
def cli(email, password_now, headless):
    password = keyring.get_password(KEYRING_SERVICE, email)
    if password == None:
        if password_now:
            print('Prompting user {} to enter password now:'.format(email))
            password = getpass.getpass(prompt='Password: ', stream=None)
        else:
            print('Prompting user {} to enter password any time.'.format(email))
            password = prompt_user_for_account_info(email)
            keyring.set_password(KEYRING_SERVICE, email, password)
    else:
        print('Password for {} retrieved from keyring!'.format(email))
    check_in_periodically(email, password, headless)


if __name__ == '__main__':
    cli()
