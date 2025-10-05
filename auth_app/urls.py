from django.urls import path
from . import views

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='login'),
    path('social-login', views.SocialLoginView.as_view(), name='social-login'),
    path('change-password', views.ChangePasswordView.as_view(), name='change-password'),
    path('password-reset-request', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset', views.PasswordResetView.as_view(), name='password-reset'),
]

