from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from main.form import MailingForm, ClientForm
from main.models import Mailing, Client, MailingLog


class MailingListView(ListView):
    model = Mailing
    extra_context = {
        'title': 'Рассылки'
    }

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists() or user.is_superuser:
            queryset = super().get_queryset()
        else:
            queryset = super().get_queryset().filter(
                mailing_owner=user.pk
            )
        return queryset


class MailingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    extra_context = {
        'title': 'Добавление рассылки'
    }

    def test_func(self):
        user = self.request.user
        if not user.groups.filter(name='manager').exists() and not user.groups.filter(name='content_manager').exists():
            return True
        return False

    def get_success_url(self):
        return reverse('main:mailing_detail', args=[self.object.pk])

    def form_valid(self, form):
        user = self.request.user
        self.object = form.save()
        self.object.mailing_owner = user
        self.object.save()
        return redirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def handle_no_permission(self):
        return redirect(reverse_lazy('main:mailing_list'))


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    extra_context = {
        'title': 'Изменение рассылки'
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        user = self.request.user
        mailing = self.get_object()

        if mailing.mailing_owner == user or user.groups.filter(name='manager').exists() or user.is_superuser:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse_lazy('main:mailing_list'))

    def get_success_url(self):
        return reverse('main:mailing_detail', args=[self.object.pk])


class MailingDetailView(DetailView, UserPassesTestMixin):
    model = Mailing
    extra_context = {
        'title': 'Информация о рассылке'
    }

    def test_func(self):
        user = self.request.user
        mailing = self.get_object()

        if mailing.mailing_owner == user or user.groups.filter(name='manager').exists() or user.is_superuser:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse_lazy('main:mailing_list'))


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy('main:mailing_list')
    extra_context = {
        'title': 'Удаление рассылки'
    }

    def test_func(self):
        user = self.request.user
        mailing = self.get_object()

        if mailing.mailing_owner == user or user.is_superuser:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse_lazy('main:mailing_list'))


@login_required
def mailing_logs(request, mailing_id):
    mailing = get_object_or_404(Mailing, pk=mailing_id)
    logs = MailingLog.objects.filter(log_mailing=mailing).order_by('-created_time')

    if (mailing.mailing_owner == request.user or request.user.is_superuser
            or request.user.groups.filter(name='manager').exists()):
        context = {
            'mailing': mailing,
            'logs': logs,
        }
        return render(request, 'main/mailing_logs.html', context)
    else:
        return redirect("mail:mailing_list")


class ClientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Client
    extra_context = {
        'title': 'Мои клиенты'
    }

    def test_func(self):
        user = self.request.user
        if not user.is_staff or user.is_superuser:
            return True
        return False

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = super().get_queryset()
        else:
            queryset = super().get_queryset().filter(
                client_owner=user.pk
            )
        return queryset

    def handle_no_permission(self):
        return redirect(reverse_lazy('main:mailing_list'))


class ClientCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Client
    form_class = ClientForm
    extra_context = {
        'title': 'Добавление клиента'
    }

    def test_func(self):
        user = self.request.user
        if not user.is_staff or user.is_superuser:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse_lazy('main:mailing_list'))

    def get_success_url(self):
        return reverse('main:client_detail', args=[self.object.pk])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.client_owner = self.request.user
        self.object.save()
        return redirect(self.get_success_url())


class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Client
    form_class = ClientForm
    extra_context = {
        'title': 'Изменение клиента'
    }

    def test_func(self):
        user = self.request.user
        mailing = self.get_object()

        if mailing.client_owner == user or user.is_staff:
            return True
        return False

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.client_owner != self.request.user and not self.request.user.is_staff:
            raise Http404
        return self.object

    def handle_no_permission(self):
        return redirect(reverse_lazy('main:client_list'))

    def get_success_url(self):
        return reverse('main:client_detail', args=[self.object.pk])


class ClientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Client
    extra_context = {
        'title': 'Информация о клиенте'
    }

    def test_func(self):
        user = self.request.user
        if not user.is_staff or user.is_superuser:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse_lazy('main:mailing_list'))


class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('main:client_list')
    extra_context = {
        'title': 'Удаление клиента'
    }

    def test_func(self):
        user = self.request.user
        if not user.is_staff or user.is_superuser:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse_lazy('main:mailing_list'))