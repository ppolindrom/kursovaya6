
from django.urls import path
from users.apps import UsersConfig
from users.views import (LoginView, LogoutView, RegisterView, ProfileView, generate_new_password,
                         ConfirmRegistrationView, reset_password, UsersListView, UsersDetailView, UsersDeleteView,
                         toggle_status)

app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/genpassword/', generate_new_password, name='generate_new_password'),
    path('confirm/<str:vrf_token>/', ConfirmRegistrationView.as_view(), name='confirm'),
    path('reset_password/', reset_password, name='reset_password'),
    path('users_list/', UsersListView.as_view(), name='users_list'),
    path('users/<int:pk>/detail/', UsersDetailView.as_view(), name='detail'),
    path('users/<int:pk>/delete/', UsersDeleteView.as_view(), name='delete'),
    path('user/toggle_status/<int:pk>', toggle_status, name='toggle_status'),
]