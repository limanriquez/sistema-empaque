from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from inventario.views import home, error_404, error_500


handler404 = error_404
handler500 = error_500


class PasswordResetViewHTML(auth_views.PasswordResetView):
    email_template_name = "registration/password_reset_email.html"
    html_email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"


urlpatterns = [

    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "",
        home,
        name="home",
    ),

    # path("", include("personas.urls")),

   
    path(
        "",
        include("usuarios.urls", namespace="usuarios"),
    ),

    path(
        "",
        include("empresa.urls", namespace="empresa"),
    ),

    path(
        "",
        include("catalogos.urls", namespace="catalogos"),
    ),

    # path("", include("users.urls", namespace="users")),

    path(
        "user/",
        include("users.urls", namespace="user"),
    ),

    path(
        "",
        include("authentication.urls", namespace="authentication"),
    ),

    # ========================================================
    # RESTABLECIMIENTO DE CONTRASEÑA
    # ========================================================

    path(
        "password_reset/",
        PasswordResetViewHTML.as_view(
            template_name="registration/password_reset_form.html",
        ),
        name="password_reset",
    ),

    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

]