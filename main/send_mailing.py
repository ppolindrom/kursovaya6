import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
import smtplib
from email.mime.text import MIMEText
import datetime
from smtplib import SMTPException
from main.models import Mailing, MailingLog
import pytz
from decouple import config


def send_mails():
    now = datetime.datetime.now()
    for mailing in Mailing.objects.filter(mailing_status=Mailing.STATUS_STARTED):
        for mailing_client in mailing.mailing_clients.all():
            mailing_log = MailingLog.objects.filter(log_client=mailing_client, log_mailing=mailing)
            if mailing_log.exists():
                last_try = mailing_log.order_by('-created_time').first()
                desired_timezone = pytz.timezone('Europe/Moscow')
                last_try_date = last_try.created_time.astimezone(desired_timezone)
                if mailing.PERIOD_DAILY:
                    if (now.date() - last_try_date.date()).days >= 1:
                        send_email(mailing, mailing_client)
                elif mailing.PERIOD_WEEKLY:
                    if (now.date() - last_try_date.date()).days >= 7:
                        send_email(mailing, mailing_client)
                elif mailing.PERIOD_MONTHLY:
                    if (now.date() - last_try_date.date()).days >= 30:
                        send_email(mailing, mailing_client)
            else:
                send_email(mailing, mailing_client)



def send_email(mailing, mailing_client):
    """Функция по отправке сообщений пользователю"""
    file_content = mailing.body

    msg = MIMEText(file_content)
    msg['Subject'] = mailing.subject
    msg['From'] = config('EMAIL_HOST_USER')
    msg['To'] = mailing_client.email

    smtp_server = config('EMAIL_HOST')
    smtp_port = config('EMAIL_PORT')
    smtp_username = config('EMAIL_HOST_USER')
    smtp_password = config('EMAIL_HOST_PASSWORD')

    s = smtplib.SMTP_SSL(smtp_server, smtp_port)
    s.login(smtp_username, smtp_password)
    try:
        s.sendmail('polinaskypro@yandex.ru', [mailing_client.email], msg.as_string())
        s.quit()
        MailingLog.objects.create(
            log_status=MailingLog.STATUS_OK,
            log_client=mailing_client,
            log_mailing=mailing,
            response='отправлено'
        )
    except SMTPException as e:
        MailingLog.objects.create(
            log_status=MailingLog.STATUS_FAILED,
            log_client=mailing_client,
            log_mailing=mailing,
            response=e
        )




if __name__ == '__main__':
    send_mails()