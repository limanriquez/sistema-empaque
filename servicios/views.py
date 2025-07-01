from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
# Create your views here.
import ftplib


def loadImage(request):
	return render(request, 'servicios/cargar_archivo_ftp.html',{
			'title':"Mis Dulces VI"})

def subirImagenFtp(request):
    if request.method != 'POST' or 'imagen' not in request.FILES:
        return JsonResponse({'status': 400, 'mensaje': 'Falta imagen o método no permitido'}, status=400)

    imagen = request.FILES['imagen']
    nombre_archivo = imagen.name  # Nombre de la imagen
    tipo = obtener_tipo_imagen(imagen.file)

    # if tipo not in ['jpg', 'png']:
    #     return JsonResponse({'status': 400, 'mensaje': 'Tipo de imagen no permitido'}, status=400)
    # else:
    try:
        # Conexión FTP
        servidor = 'ftp.niidia.com'
        usuario = 'servicios@niidia.com'  # 'dnhrcomm'
        contrasena = 'WkNKypDag*Z0y!1j'  # 'YlE1Fr8$m2jA'
        # directorio_remoto = 'niidia.com/data/'  # Directorio donde se suben las imágenes

        # Conectarse al servidor FTP
        ftp = ftplib.FTP(servidor)
        ftp.login(usuario, contrasena)
        # ftp.mkd("data")
        # ftp.cwd(directorio_remoto)  # Cambiar al directorio deseado

        # Subir la imagen
        ftp.storbinary(f'STOR {nombre_archivo}', imagen.file)

        # Nombre del archivo .txt donde se guardarán los registros de imágenes
        archivo_txt = 'imagenes_subidas.txt'

        # Leer el archivo .txt si ya existe, sino crear uno nuevo
        try:
            # Descargar el archivo existente (si lo hay) para agregar la nueva imagen
            ftp.retrbinary(f"RETR {archivo_txt}", open(archivo_txt, 'wb').write)
        except ftplib.error_perm:
            # Si el archivo no existe, no hace nada
            pass

        # Agregar el nombre de la nueva imagen al archivo .txt
        with open(archivo_txt, 'a') as f:
            f.write(f'{nombre_archivo}\n')

        # Subir el archivo .txt con el registro de imágenes
        ftp.storbinary(f'STOR {archivo_txt}', open(archivo_txt, 'rb'))

        # Cerrar la conexión FTP
        ftp.quit()

        return JsonResponse({'status': 200, 'nombre_archivo': nombre_archivo, 'mensaje': 'Imagen subida correctamente y archivo .txt actualizado'})

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
