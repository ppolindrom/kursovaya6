from django import forms

from main.models import Mailing, Client


class VisualMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class MailingForm(VisualMixin, forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_staff:
            mailing_owner = self.instance.mailing_owner
            self.fields['mailing_clients'].queryset = Client.objects.filter(client_owner=mailing_owner)
        else:
            self.fields['mailing_clients'].queryset = Client.objects.filter(client_owner=user)

    class Meta:
        model = Mailing
        exclude = ('mailing_owner',)


class ClientForm(VisualMixin, forms.ModelForm):
    class Meta:
        model = Client
        exclude = ('client_owner',)