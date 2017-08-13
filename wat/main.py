import click
import os
import getpass
import sys
import keyring
import traceback
from time import time, sleep
from selenium import webdriver
from . web import *
from . utils import *


def login_and_attempt_operation(website, email, password, headless):
    wd = webdriver.PhantomJS() if headless else webdriver.Firefox()
    wd.set_window_size(1920, 1080)
    status = Status.UNEXPECTED_ERROR
    try:
        status = website.login(wd, email, password)
        if not status == Status.OK:
            wd.quit()
            return status
    except Exception:
        status = Status.PROBLEM_ACCESSING_LOGIN
        traceback.print_exc()
    else:
        status = website.operate(wd)
    finally:
        wd.quit()
        return status


def operate_periodically(website, email, password, headless, stuck_time_threshold, error_time_threshold, period):
    last_operation_time_file = 'Last_{}_{}.txt'.format(website.name, website.operation)
    if not os.path.exists(last_operation_time_file):
        last_operation_time = time()
    else:
        with open(last_operation_time_file) as f:
            last_operation_time = float(f.readlines()[0].strip())
    while True:
        try:
            status = login_and_attempt_operation(website, email, password, headless)
            current_time = time()
            print('{} {} {}'.format(current_time, format_time(current_time), status))
            if status == Status.SUCCESSFUL_OPERATION:
                last_operation_time = current_time
                with open(last_operation_time_file, 'w') as f:
                    f.write('{}\n{}'.format(last_operation_time, format_time(last_operation_time)))
            elif status == Status.OPERATION_UNNECESSARY:
                if current_time - last_operation_time >= stuck_time_threshold:
                    send_email(email, email,
                        '{} {} status might be stuck!'.format(website.name, website.operation))
            else:
                if current_time - last_operation_time >= error_time_threshold:
                    send_email(email, email,
                        '{} {} encountered error: {}'.format(website.name, website.operation, status))
        except:
            print('FATAL_ERROR!')
            traceback.print_exc()
            send_email(email, email,
                '{} {} fatal error: {}'.format(website.name, website.operation, sys.exc_info()))
        sleep(3600 * period)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--website-name', '-w', type=str, required=True,
              help='Website to be operated on [xiami|noip].')
@click.option('--user-email', '-u', type=str, required=True,
              help='Web account email address (also for sending/receiving error notifications).')
@click.option('--password-now/--no-password-now', default=True,
              help='''If now, prompt user on cmd-line for password (thus, should not be run in background);
                      otherwise, open a gui password prompt that can be filled later.''')
@click.option('--use-keyring/--no-use-keyring', default=True,
              help='Indicate whether or not system keyring should be used for looking up/storing password.')
@click.option('--headless/--no-headless', default=True,
              help='Indicate whether or not headless mode should be used.')
@click.option('--num-hosts', '-n', type=int, default=None,
              help='Number of free hostnames (if No-IP free hostnames refreshing is intended).')
@click.option('--stuck-time-threshold', '-s', type=int, default=None,
              help='Operation status stuck time threshold (in hours) before user is notified via email.')
@click.option('--error-time-threshold', '-e', type=int, default=None,
              help='Operation error time threshold (in hours) before user is notified via email.')
@click.option('--period', '-p', type=int, default=None,
              help='Automation operation attempt period (in hours).')
def cli(website_name, user_email, password_now, use_keyring, headless, num_hosts, stuck_time_threshold, error_time_threshold, period):
    WS = None
    if website_name.lower().strip() == 'xiami':
        ws = XiaMi()
        WS = XiaMi
    elif website_name.lower().strip() == 'noip':
        ws = NoIP(num_hosts if num_hosts else NoIP.DEFAULT_NUM_HOSTS)
        WS = NoIP
    else:
        raise NotImplementedError

    stuck_time_threshold = stuck_time_threshold if stuck_time_threshold else WS.DEFAULT_OPERATION_STATUS_STUCK_THRESHOLD
    error_time_threshold = error_time_threshold if error_time_threshold else WS.DEFAULT_OPERATION_ERROR_TIME_THRESHOLD
    period = period if period else WS.DEFAULT_OPERATION_ATTEMPT_PERIOD

    password = keyring.get_password('{}_{}'.format(ws.name, ws.operation), user_email) if use_keyring else None
    if password:
        print('{} password for {} retrieved from keyring!'.format(ws.name, user_email))
    else:
        if password_now:
            print('Prompting user {} to enter {} password now on cmd-line:'.format(user_email, ws.name))
            password = getpass.getpass(prompt='Password: ', stream=None)
        else:
            print('Prompting user {} to enter {} password in GUI window...'.format(user_email, ws.name))
            password = prompt_user_for_password(ws.name, user_email)
        if use_keyring:
            keyring.set_password('{}_{}'.format(ws.name, ws.operation), user_email, password)
            print('{} password for {} saved in keyring!'.format(ws.name, user_email))

    operate_periodically(ws, user_email, password, headless, stuck_time_threshold, error_time_threshold, period)


if __name__ == '__main__':
    cli()
