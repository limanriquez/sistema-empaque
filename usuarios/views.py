from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
from usuarios.models import *

@login_required()
def usuarios(request):
	return render(request, 'usuarios/superusuario.html',{
			'title':"Super Usuario"})

@login_required()
def getSuperUsuarioPorEmpresa(request):
	superUsuario_json = []
	superUsuario = SuperUsuario.objects.filter(User = request.user).first()
	print(request.user.is_staff)
	if superUsuario:
		tmp = {
			'Id': superUsuario.Id,
			'TokenCondusef': superUsuario.TokenCondusef,
			'Nombre': superUsuario.Nombre,
			'Password': superUsuario.Password,
			'Token': superUsuario.Token,
		}
		superUsuario_json.append(tmp)
	return JsonResponse(superUsuario_json, safe = False)