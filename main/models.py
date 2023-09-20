from django.db import models

from config import settings

NULLABLE = {
    'null': True,
    'blank': True
}


class Client(models.Model):
    email = models.EmailField(verbose_name='почта')
    first_name = models.CharField(max_length=100, **NULLABLE, verbose_name='имя')
    last_name = models.CharField(max_length=100, **NULLABLE, verbose_name='фамилия')
    surname = models.CharField(max_length=100, **NULLABLE, verbose_name='отчество')
    comment = models.TextField(**NULLABLE, verbose_name='комментарий')
    client_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='владелец', **NULLABLE)

    def __str__(self):
        return f'{self.email} ({self.first_name} {self.last_name})'

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'


class Mailing(models.Model):
    PERIOD_DAILY = 'daily'
    PERIOD_WEEKLY = 'weekly'
    PERIOD_MONTHLY = 'monthly'

    PERIODS = (
        (PERIOD_DAILY, 'Ежедневная'),
        (PERIOD_WEEKLY, 'Раз в неделю'),
        (PERIOD_MONTHLY, 'Раз в месяц'),
    )

    STATUS_CREATED = 'created'
    STATUS_STARTED = 'started'
    STATUS_DONE = 'done'
    STATUSES = (
        (STATUS_STARTED, 'Запущена'),
        (STATUS_CREATED, 'Создана'),
        (STATUS_DONE, 'Завершена'),
    )

    send_time = models.TimeField(verbose_name='время рассылки')
    send_frequency = models.CharField(max_length=20, choices=PERIODS, verbose_name='периодичность')
    mailing_status = models.CharField(max_length=20, choices=STATUSES, default=STATUS_CREATED, verbose_name='статус')
    mailing_clients = models.ManyToManyField(Client, **NULLABLE, verbose_name='подписчики')
    subject = models.CharField(max_length=200, verbose_name='тема письма')
    body = models.TextField(verbose_name='тело письма')
    mailing_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='владелец', **NULLABLE)

    def __str__(self):
        return f"Рассылка {self.subject} в {self.send_time} ({self.send_frequency})"

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        permissions = [
            ('set_mailing_status', 'Can change the status of mailing'),
        ]


class MailingLog(models.Model):
    STATUS_OK = 'ok'
    STATUS_FAILED = 'failed'
    STATUSES = (
        (STATUS_OK, 'Успешно'),
        (STATUS_FAILED, 'Ошибка'),
    )

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='дата и время последней попытки')
    log_status = models.CharField(max_length=20, choices=STATUSES, verbose_name='статус попытки')
    log_client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='подписчик')
    log_mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='рассылка')
    response = models.TextField(**NULLABLE, verbose_name='ответ сервера')

    def __str__(self):
        return f"{self.log_client} - {self.log_mailing} ({self.log_status}) в {self.created_time}"

    class Meta:
        verbose_name = 'лог'
        verbose_name_plural = 'логи'