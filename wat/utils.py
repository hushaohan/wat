import smtplib
from email.mime.text import MIMEText
from datetime import datetime


def send_email(me, you, msg_content):
    msg = MIMEText(msg_content)
    msg['Subject'] = msg_content
    msg['From'] = me
    msg['To'] = you
    print('mail')
    sender = smtplib.SMTP('localhost')
    sender.sendmail(me, [you], msg.as_string())
    sender.quit()


def format_time(t):
    return datetime.fromtimestamp(t).strftime('%Y-%m-%d_%H:%M:%S')


def prompt_user_for_password(site_name, email):
    import tkinter
    import tkinter.simpledialog
    tkinter.Tk().withdraw()
    return tkinter.simpledialog.askstring('Password', '{} password for {}:'.format(site_name, email), show='*')
