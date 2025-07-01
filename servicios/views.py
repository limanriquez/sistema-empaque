from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import hashlib
import os
# Create your views here.
import ftplib


def loadImage(request):
	return render(request, 'servicios/cargar_archivo_ftp.html',{
			'title':"Mis Dulces VI"})

import ftplib
from django.http import JsonResponse
# from .utils import obtener_tipo_imagen  # ← Comentado: no lo necesitas si no validas el tipo

def subirImagenFtp(request):
    if request.method != 'POST' or 'imagen' not in request.FILES:
        return JsonResponse({'status': 400, 'mensaje': 'Falta imagen o método no permitido'}, status=400)

    imagen = request.FILES['imagen']

    # Leer contenido para el hash y luego volver a colocar el puntero
    contenido = imagen.read()
    hash_completo = hashlib.sha256(contenido).hexdigest()
    hash_corto = hash_completo[:16]  # 16 caracteres es un buen balance

    # Obtener extensión
    _, extension = os.path.splitext(imagen.name)
    nombre_archivo = f"{hash_corto}{extension}"

    # Volver a posicionar el cursor para poder leer el archivo al subir
    imagen.seek(0)

    try:
        servidor = 'ftp.niidia.com'
        usuario = 'servicios@niidia.com'
        contrasena = 'WkNKypDag*Z0y!1j'
        # directorio_remoto = 'niidia.com/data/'

        ftp = ftplib.FTP(servidor)
        ftp.login(usuario, contrasena)
        # ftp.cwd(directorio_remoto)

        ftp.storbinary(f'STOR {nombre_archivo}', imagen.file)

        archivo_txt = 'imagenes_subidas.txt'
        try:
            ftp.retrbinary(f"RETR {archivo_txt}", open(archivo_txt, 'wb').write)
        except ftplib.error_perm:
            pass

        with open(archivo_txt, 'a') as f:
            f.write(f'{nombre_archivo}\n')

        ftp.storbinary(f'STOR {archivo_txt}', open(archivo_txt, 'rb'))
        ftp.quit()

        return JsonResponse({
            'status': 200,
            'nombre_archivo': nombre_archivo,
            'mensaje': 'Imagen subida correctamente y archivo .txt actualizado'
        })

    except Exception as e:
        return JsonResponse({'status': 500, 'error': str(e)}, status=500)




def obtener_tipo_imagen(file_obj):
	inicio = file_obj.read(10)  # Leer primeros 10 bytes
	file_obj.seek(0)  # Volver al inicio del archivo después de leer

	if inicio.startswith(b'\xff\xd8\xff'):
		return 'jpg'
	elif inicio.startswith(b'\x89PNG\r\n\x1a\n'):
		return 'png'
	else:
		return 'desconocido'
