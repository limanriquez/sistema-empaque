from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordChangeDoneView

app_name = 'users'  # Asegúrate de que el namespace esté configurado correctamente.

urlpatterns = [
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='user/password_change.html',
        success_url=None  # Evita redirigir a otra página después de un cambio exitoso.
    ), name='password_change'),
]