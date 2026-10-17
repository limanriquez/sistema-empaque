from django.urls import path
from . import views

urlpatterns = [
    # Crear registros de auditoría desde Excel
    path(
        "crear/",
        views.crear_registro,
        name="crear_registro",
    ),

    # Validar usuario y contraseña desde Excel
    path(
        "login-excel/",
        views.validar_login_excel,
        name="validar_login_excel",
    ),

    path(
        "consultar/<int:id>/",
        views.consultar_registro,
        name="consultar_registro",
    ),
]