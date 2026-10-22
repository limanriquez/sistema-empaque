
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authentication.views import *

app_name = 'authentication'

router = DefaultRouter()

# router.register(r'accounts', AccountViewSet)
# router.register(r'companies', CompanyViewSet)
# router.register('personas', PersonasViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),

    # Autenticación
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

    # Restablecimiento de contraseña: envío del correo
    path(
        'accounts/password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='authentication/password_reset_form.html',
            email_template_name='registration/password_reset_email.txt',
            html_email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
        ),
        name='password_reset',
    ),

    # Confirmación de envío
    path(
        'accounts/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),

    # Formulario para establecer la nueva contraseña
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),

    # Confirmación de contraseña restablecida
    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
]
