import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from config import settings
from users.form import UserForm, UserProfileForm
from users.models import User
from django.contrib import messages
from django.views.generic import ListView
from users.utils import send_mail


class LoginView(BaseLoginView):
    template_name = 'users/login.html'


class LogoutView(BaseLogoutView):
    pass


class RegisterView(CreateView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/register.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        vrf_token = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        confirm_url = self.request.build_absolute_uri(reverse('users:confirm', args=[vrf_token]))
        user.vrf_token = vrf_token
        user.save()
        to = user.email
        subject = 'Регистрация в нашем проекте MailingAgent!'
        message = f'Для регистрации перейдите по ссылке {confirm_url}'
        send_mail(
            theme=subject,
            message=message,
            to=to
        )
        return super().form_valid(form)


class ConfirmRegistrationView(View):
    def get(self, request, vrf_token):
        try:
            user = User.objects.get(vrf_token=vrf_token)
            user.is_active = True
            user.vrf_token = None
            user.save()
        except User.DoesNotExist:
            messages.error(request, "Ошибка: Пользователь с указанным "
                                    "токеном не найден. Пройдите регистрацию снова.")
        return redirect('users:login')


class ProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def test_func(self):
        user = self.request.user
        object = self.get_object()
        if user.is_superuser or user.email == object.email:
            return True
        return False

    def handle_no_permission(self):
        user = self.request.user
        if user.is_staff:
            return redirect(reverse_lazy('users:users_list'))
        else:
            return redirect(reverse_lazy('agent:mailing_list'))

    def get_object(self, queryset=None):
        return self.request.user


@login_required
def generate_new_password(request):
    new_password = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    to = request.user.email
    subject = 'Вы сменили пароль!'
    message = f'Ваш новый пароль: {new_password}'
    from_email = settings.EMAIL_HOST_USER
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[to]
    )
    request.user.set_password(new_password)
    request.user.save()
    return redirect(reverse('catalog:home'))


def reset_password(request):
    """Сгенерировать новый пароль для пользователя если пароль забыли"""
    if request.method == 'POST':
        user_email = request.POST.get('email')
        try:
            user = User.objects.get(email=user_email)
            new_password = "".join([str(random.randint(0, 9)) for _ in range(12)])
            user.set_password(new_password)
            user.save()

            subject = "Смена пароля на платформе MailingAgent!"
            message = f"Ваш новый пароль: {new_password}"
            from_email = settings.EMAIL_HOST_USER
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[user_email]
            )
            return redirect(reverse("users:login"))
        except User.DoesNotExist:
            return render(request, 'users/change_password.html', {'error_message': 'User not found'})
    return render(request, 'users/change_password.html')


class UsersListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    permission_required = 'users.view_user'
    success_url = reverse_lazy('agent:mailing_list')
    extra_context = {
        'title': 'Пользователи сервиса'
    }

    def get_queryset(self):
        queryset = User.objects.filter(
            is_staff=False
        )
        return queryset

    def test_func(self):
        user = self.request.user
        # logger.debug(f"User {user.username} has permissions: {user.get_all_permissions()}")
        if user.is_staff:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse_lazy('agent:mailing_list'))


class UsersDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    extra_context = {
        'title': 'Информация о пользователе'
    }

    def test_func(self):
        user = self.request.user
        object = self.get_object()
        if user.is_staff or user.email == object.email:
            return True
        return False

    def handle_no_permission(self):
        return redirect(reverse_lazy('agent:mailing_list'))


class UsersDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    extra_context = {
        'title': 'Удаление пользователя'
    }

    def test_func(self):
        user = self.request.user
        object = self.get_object()
        if not user.is_staff or user.is_superuser or user.email == object.email:
            return True
        return False

    def handle_no_permission(self):
        user = self.request.user
        if user.is_staff:
            return redirect(reverse_lazy('users:users_list'))
        else:
            return redirect(reverse_lazy('users:register'))

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse('users:users_list')
        else:
            return reverse('users:login')

@login_required(login_url='users:login')
def toggle_status(request, pk):
    if request.user.is_staff:
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()

        if user.is_active:
            messages.success(request, f"Пользователь {user.email} успешно активирован.")
        else:
            messages.success(request, f"Пользователь {user.email} успешно заблокирован.")
    else:
        messages.error(request, "У вас нет прав для выполнения этой операции.")

    return redirect('users:detail', pk=pk)