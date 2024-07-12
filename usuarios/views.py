from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required()
def usuarios(request):
	return render(request, 'usuarios/superusuario.html',{
			'title':"Super Usuario"})
