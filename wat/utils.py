import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import re


def send_email(me, you, msg_content):
    msg = MIMEText(msg_content)
    msg['Subject'] = msg_content
    msg['From'] = me
    msg['To'] = you
    print('mail')
    sender = smtplib.SMTP('localhost')
    sender.sendmail(me, [you], msg.as_string())
    sender.quit()


def deliver_notification(method, from_addr, to_addr, msg_content):
    if method == 'beep':
        print(msg_content)
        print('\a')
    elif method == 'email':
        send_email(from_addr, to_addr, msg_content)


def format_time(t):
    return datetime.fromtimestamp(t).strftime('%Y-%m-%d_%H:%M:%S')


def prompt_user_for_password(site_name, email):
    import tkinter
    import tkinter.simpledialog
    tkinter.Tk().withdraw()
    return tkinter.simpledialog.askstring(
        'Password', '{} password for {}:'.format(site_name, email), show='*'
    )


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)
