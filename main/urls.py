from django.urls import path
from main.apps import MainConfig
from main.views import (MailingListView, MailingCreateView, MailingUpdateView, MailingDetailView, MailingDeleteView,
                        ClientListView, ClientCreateView, ClientUpdateView, ClientDetailView, ClientDeleteView,
                        mailing_logs)

app_name = MainConfig.name

urlpatterns = [
    path('', MailingListView.as_view(), name='mailing_list'),
    path('mailing_create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing/<int:pk>/detail/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailing/<int:mailing_id>/logs', mailing_logs, name='mailing_logs'),
    path('client/', ClientListView.as_view(), name='client_list'),
    path('client_create/', ClientCreateView.as_view(), name='client_create'),
    path('client/<int:pk>/update/', ClientUpdateView.as_view(), name='client_update'),
    path('client/<int:pk>/detail/', ClientDetailView.as_view(), name='client_detail'),
    path('client/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
]
