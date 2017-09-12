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


wd = None


def attempt(website, username, password, headless, persistent_session):
    global wd
    if wd is None:
        wd = webdriver.PhantomJS() if headless else webdriver.Firefox()
    wd.set_window_size(1920, 1080)

    try:
        status = website.login(wd, username, password)
        if not status == Status.OK:
            if not persistent_session:
                wd.quit()
                wd = None
            return status
    except Exception:
        status = Status.PROBLEM_ACCESSING_LOGIN
        traceback.print_exc()
    else:
        status = website.operate(wd)
    finally:
        if not persistent_session:
            wd.quit()
            wd = None
        return status


def attempt_periodically(
        website,
        username,
        password,
        email,
        headless,
        persistent_session,
        stuck_time_threshold,
        error_time_threshold,
        notification_method,
        period):
    last_operation_time_file = 'Last_{}_{}.txt'.format(
        website.name, website.operation
    )
    if not os.path.exists(last_operation_time_file):
        last_operation_time = time()
    else:
        with open(last_operation_time_file) as f:
            last_operation_time = float(f.readlines()[0].strip())
    while True:
        try:
            status = attempt(
                website, username, password, headless, persistent_session
            )
            current_time = time()
            print('{} {} {}'.format(
                current_time, format_time(current_time), status)
            )
            if status == Status.SUCCESSFUL_OPERATION:
                last_operation_time = current_time
                with open(last_operation_time_file, 'w') as f:
                    f.write('{}\n{}'.format(
                        last_operation_time, format_time(last_operation_time))
                    )
            elif status == Status.OPERATION_UNNECESSARY:
                if current_time - last_operation_time >= stuck_time_threshold:
                    deliver_notification(
                        notification_method,
                        email,
                        email,
                        '{} {} status might be stuck!'.format(
                            website.name, website.operation)
                    )
            else:
                if current_time - last_operation_time >= error_time_threshold:
                    deliver_notification(
                        notification_method,
                        email,
                        email,
                        '{} {} encountered error: {}'.format(
                            website.name, website.operation, status)
                    )
        except:
            print('FATAL_ERROR!')
            traceback.print_exc()
            deliver_notification(
                notification_method,
                email,
                email,
                '{} {} fatal error: {}'.format(
                    website.name, website.operation, sys.exc_info()))
        sleep(period)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--website-name', '-w', type=str, required=True,
              help='Website to be operated on [xiami|noip|ddc].')
@click.option('--username', '-u', type=str, required=True,
              help='The username for the web account.')
@click.option('--email', '-e', type=str, default=None,
              help=('Email address for error notifications '
                    '(can be omitted if username is the intended email).'))
@click.option('--password-now/--no-password-now', default=True,
              help=('If now, prompt user on cmd-line for password '
                    '(thus, should not be run in background); otherwise, '
                    'open a gui password prompt that can be filled later.'))
@click.option('--use-keyring/--no-use-keyring', default=True,
              help=('Indicate whether or not system keyring should '
                    'be used for looking up/storing password.'))
@click.option('--headless/--no-headless', default=True,
              help='Indicate whether or not headless mode should be used.')
@click.option('--persistent-session', '-s', is_flag=True,
              help=('Indicate whether to use a single persistent-session '
                    'for all operations.'))
@click.option('--stuck-time-threshold', type=int, default=None,
              help=('Operation status stuck time threshold (in hours) '
                    'before user is notified via email.'))
@click.option('--error-time-threshold', type=int, default=None,
              help=('Operation error time threshold (in hours) '
                    'before user is notified via email.'))
@click.option('--notification-method', '-n', type=str, default='email',
              help='Notification method [email|beep] upon abnormalities.')
@click.option('--force', '-f', is_flag=True,
              help='Force notification, headless, and session modes.')
@click.option('--period', '-p', type=int, default=None,
              help='Automation operation attempt period (in hours).')
def cli(
        website_name,
        username,
        email,
        password_now,
        use_keyring,
        headless,
        persistent_session,
        stuck_time_threshold,
        error_time_threshold,
        notification_method,
        force,
        period):
    if not email:
        if is_valid_email(username):
            email = username
        else:
            print('No valid email provided, error notification disabled.')

    if website_name.lower().strip() == 'xiami':
        WS = XiaMi
    elif website_name.lower().strip() == 'noip':
        WS = NoIP
    elif website_name.lower().strip() == 'ddc':
        WS = DDC
        # the website uses various random verification methods
        # which require occasional human intervention
        if not force:
            if headless:
                headless = False
                print((
                    'Headless mode disabled for DDC. '
                    'Use --force to override.'
                ))
            if not persistent_session:
                persistent_session = True
                print((
                    'Persistent session mode enabled for DDC. '
                    'Use --force to override.'
                ))
            if notification_method == 'email':
                notification_method = 'beep'
                print((
                    'Notification set to beep mode for DDC. '
                    'Use --force to override.'
                ))
    else:
        raise NotImplementedError

    ws = WS()
    stuck_time_threshold = (
        stuck_time_threshold
        if stuck_time_threshold
        else WS.DEFAULT_OPERATION_STATUS_STUCK_THRESHOLD
    )
    error_time_threshold = (
        error_time_threshold
        if error_time_threshold
        else WS.DEFAULT_OPERATION_ERROR_TIME_THRESHOLD
    )
    period = period if period else WS.DEFAULT_OPERATION_ATTEMPT_PERIOD

    password = keyring.get_password(
        '{}_{}'.format(ws.name, ws.operation), username
    ) if use_keyring else None
    if password:
        print('{} password for {} retrieved from keyring!'.format(
            ws.name, username)
        )
    else:
        if password_now:
            print('Prompting user {} to enter {} password on cmd-line:'.format(
                username, ws.name)
            )
            password = getpass.getpass(prompt='Password: ', stream=None)
        else:
            print('Prompting user {} to enter {} password in GUI...'.format(
                username, ws.name)
            )
            password = prompt_user_for_password(ws.name, username)
        if use_keyring:
            keyring.set_password(
                '{}_{}'.format(ws.name, ws.operation), username, password
            )
            print('{} password for {} saved in keyring!'.format(
                ws.name, username)
            )

    attempt_periodically(
        ws,
        username,
        password,
        email,
        headless,
        persistent_session,
        stuck_time_threshold,
        error_time_threshold,
        notification_method,
        period
    )


if __name__ == '__main__':
    cli()
