
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import RegistroAuditoria

import json
from django.contrib.auth import authenticate

from django.views.decorators.http import require_GET
from .models import RegistroAuditoria

TIPOS_PERMITIDOS = {
    "HALLAZGO",
    "EVIDENCIA",
    "OBSERVACION",
    "RECOMENDACION",
    "NOTA",
    "OTRO",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@csrf_exempt
@require_POST
def crear_registro(request):
    """
    API para recibir registros de auditoría desde Excel.
    No requiere sesión ni token de autenticación.
    """

    id_revision = request.POST.get("id_revision", "").strip()
    id_criterio = request.POST.get("id_criterio", "").strip()
    tipo = request.POST.get("tipo", "").strip().upper()

    observacion = request.POST.get("observacion", "")
    recomendacion = request.POST.get("recomendacion", "")
    notas = request.POST.get("notas", "")
    status = request.POST.get("status", "true").strip().lower()

    if not id_revision or not id_criterio:
        return JsonResponse({
            "ok": False,
            "error": "id_revision e id_criterio son obligatorios.",
        }, status=400)

    if tipo not in TIPOS_PERMITIDOS:
        return JsonResponse({
            "ok": False,
            "error": "Tipo de registro no válido.",
            "tipos_permitidos": sorted(TIPOS_PERMITIDOS),
        }, status=400)

    if status not in {"true", "false", "1", "0"}:
        return JsonResponse({
            "ok": False,
            "error": "status debe ser true o false.",
        }, status=400)

    archivo = request.FILES.get("archivo")

    if archivo:
        if archivo.size > MAX_FILE_SIZE:
            return JsonResponse({
                "ok": False,
                "error": "El archivo supera el límite de 10 MB.",
            }, status=413)

        nombre = os.path.basename(archivo.name)

        if nombre != archivo.name or nombre in {"", ".", ".."}:
            return JsonResponse({
                "ok": False,
                "error": "Nombre de archivo no válido.",
            }, status=400)

    registro = RegistroAuditoria.objects.create(
        id_revision=id_revision,
        id_criterio=id_criterio,
        tipo=tipo,
        observacion=observacion,
        recomendacion=recomendacion,
        notas=notas,
        status=status in {"true", "1"},
        archivo=archivo,
    )

    return JsonResponse({
        "ok": True,
        "mensaje": "Registro creado correctamente.",
        "id": registro.pk,
        "id_compuesto": registro.id_compuesto,
        "tipo": registro.tipo,
    }, status=201)



@csrf_exempt
@require_POST
def validar_login_excel(request):
    """
    Valida las credenciales del usuario desde Excel.
    No utiliza tokens ni crea una sesión de Django.
    """
    try:
        datos = json.loads(request.body)

        username = datos.get("username", "").strip()
        password = datos.get("password", "")

        if not username or not password:
            return JsonResponse({
                "ok": False,
                "mensaje": "Debes ingresar usuario y contraseña."
            }, status=400)

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is None or not usuario.is_active:
            return JsonResponse({
                "ok": False,
                "mensaje": "Usuario o contraseña incorrectos."
            }, status=401)

        return JsonResponse({
            "ok": True,
            "mensaje": "Credenciales válidas.",
            "usuario": usuario.get_username()
        }, status=200)

    except (json.JSONDecodeError, TypeError):
        return JsonResponse({
            "ok": False,
            "mensaje": "Solicitud inválida."
        }, status=400)

@require_GET
def consultar_registro(request, id):
    try:
        registro = RegistroAuditoria.objects.get(pk=id)

        return JsonResponse(
            {
                "ok": True,
                "id": registro.pk,
                "id_revision": registro.id_revision,
                "id_criterio": registro.id_criterio,
                "tipo": registro.tipo,
                "observacion": registro.observacion,
                "recomendacion": registro.recomendacion,
                "notas": registro.notas,
                "status": registro.status,
                "archivo": (
                    registro.archivo.url
                    if registro.archivo
                    else None
                ),
            },
            json_dumps_params={
                "ensure_ascii": False
            },
        )

    except RegistroAuditoria.DoesNotExist:
        return JsonResponse(
            {
                "ok": False,
                "mensaje": "No se encontró el registro.",
            },
            status=404,
            json_dumps_params={
                "ensure_ascii": False
            },
        )