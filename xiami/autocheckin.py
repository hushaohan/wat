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
from enum import Enum, auto
from . config import *


class Status(Enum):
    UNEXPECTED_ERROR_WITH_CHECKIN = auto()
    ERROR_WITH_CHECKIN = auto()
    ERROR_WITH_LOGIN = auto()
    TIMED_OUT_DURING_LOGIN = auto()
    SUCCESSFULLY_CHECKED_IN = auto()
    ALREADY_CHECKED_IN = auto()


def send_email(me, you, msg_content):
    msg = MIMEText(msg_content)
    msg['Subject'] = msg_content
    msg['From'] = me
    msg['To'] = you
    print('mail')
    sender = smtplib.SMTP('localhost')
    sender.sendmail(me, [you], msg.as_string())
    sender.quit()


def wait_for_any_elements_to_load(wd, elms):
    rounds = 0
    while rounds < MAX_WEBDRIVER_LOADING_WAIT_ROUNDS:
        wd.implicitly_wait(WEBDRIVER_LOADING_WAIT_TIME)
        for elm in elms:
            if wd.find_elements_by_xpath(elm):
                return True
        rounds += 1
    return False


def login_xiami_and_attempt_check_in(wd, email, password):
    wd.get(XIAMI_LOGIN_URL)
    wd.find_elements_by_id("J_LoginSwitch")[0].click()
    wd.find_element_by_id('account').send_keys(email)
    wd.find_element_by_id('pw').send_keys(password)
    wd.find_element_by_id('submit').click()

    try:
        if not wait_for_any_elements_to_load(wd, ["//b[@class='icon tosign done']", "//b[@class='icon tosign']"]):
            return Status.ERROR_WITH_LOGIN
    except Exception:
        return Status.TIMED_OUT_DURING_LOGIN

    if wd.find_elements_by_xpath("//b[@class='icon tosign done']"):
        return Status.ALREADY_CHECKED_IN
    else:
        elms_tosign = wd.find_elements_by_xpath("//b[@class='icon tosign']")
        if len(elms_tosign) > 0:
            elms_tosign[0].click()
            if wait_for_any_elements_to_load(wd, ["//b[@class='icon tosign done']"]):
                return Status.SUCCESSFULLY_CHECKED_IN
            else:
                return Status.ERROR_WITH_CHECKIN
        else:
            return Status.UNEXPECTED_ERROR_WITH_CHECKIN


def format_time(t):
    return datetime.fromtimestamp(t).strftime('%Y-%m-%d_%H:%M:%S')


def check_in_periodically(email, password, period, headless):
    if not os.path.exists(LAST_CHECK_IN_FILE):
        last_check_in_time = time()
    else:
        with open(LAST_CHECK_IN_FILE) as f:
            last_check_in_time = float(f.readlines()[0].strip())
    while True:
        try:
            wd = webdriver.PhantomJS() if headless else webdriver.Firefox()
            status = login_xiami_and_attempt_check_in(wd, email, password)
            wd.close()
            current_time = time()
            print('{} {} {}'.format(current_time, format_time(current_time), status))
            if status == Status.SUCCESSFULLY_CHECKED_IN:
                last_check_in_time = current_time
                with open(LAST_CHECK_IN_FILE, 'w') as f:
                    f.write('{}\n{}'.format(last_check_in_time, format_time(last_check_in_time)))
            elif status == Status.ALREADY_CHECKED_IN:
                if current_time - last_check_in_time >= CHECK_IN_STATUS_STUCK_THRESHOLD:
                    send_email(email, email, 'Xiami checkin status might be stuck!')
            else:
                if current_time - last_check_in_time >= CHECK_IN_ERROR_TIME_THRESHOLD:
                    send_email(email, email, 'Xiami checkin encountered error: {}'.format(status))
        except:
            print('FATAL_ERROR: {}'.format(sys.exc_info()))
            send_email(email, email, 'Xiami checkin fatal error: {}'.format(sys.exc_info()))
        sleep(3600 * period)


def prompt_user_for_password(email):
    import tkinter
    import tkinter.simpledialog
    tkinter.Tk().withdraw()
    return tkinter.simpledialog.askstring('Password', 'Xiami password for {}:'.format(email), show='*')


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--email', '-e', type=str, required=True,
              help='Xiami account email address (also for sending/receiving error notifications)')
@click.option('--password-now/--no-password-now', default=True,
              help='''If now, prompt user on cmd-line for password (thus, should not be run in background);
                      otherwise, open a gui password prompt that can be filled later.''')
@click.option('--period', '-p', type=int, default=DEFAULT_CHECKIN_ATTEMPT_PERIOD,
              help='Checkin attempt period (in hours)')
@click.option('--use-keyring/--no-use-keyring', default=True,
              help='Indicate whether or not system keyring should be used for looking up/storing password.')
@click.option('--headless/--no-headless', default=True,
              help='Indicate whether or not headless mode should be used.')
def cli(email, password_now, period, use_keyring, headless):
    password = keyring.get_password(KEYRING_SERVICE, email) if use_keyring else None
    if password:
        print('Password for {} retrieved from keyring!'.format(email))
    else:
        if password_now:
            print('Prompting user {} to enter password now:'.format(email))
            password = getpass.getpass(prompt='Password: ', stream=None)
        else:
            print('Prompting user {} to enter password any time.'.format(email))
            password = prompt_user_for_password(email)
        if use_keyring:
            keyring.set_password(KEYRING_SERVICE, email, password)
            print('Password for {} saved in keyring!'.format(email))
    check_in_periodically(email, password, period, headless)


if __name__ == '__main__':
    cli()
