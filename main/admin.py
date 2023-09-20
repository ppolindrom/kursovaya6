from django.contrib import admin
from .models import Client, Mailing, MailingLog


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'surname', 'comment')
    search_fields = ('email',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('send_time', 'send_frequency', 'mailing_status', 'display_mailing_clients', 'subject', 'body')
    search_fields = ('send_frequency', 'mailing_status', 'mailing_clients')

    def display_mailing_clients(self, obj):
        return ', '.join([client.email for client in obj.mailing_clients.all()])

    display_mailing_clients.short_description = 'Mailing Clients'


@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ('created_time', 'log_status', 'log_client', 'log_mailing', 'response')
    search_fields = ('log_status', 'log_client', 'log_mailing')

