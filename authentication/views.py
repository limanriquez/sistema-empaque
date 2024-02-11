from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.
def login(request):
	if 'next' in request.GET:
		next = request.GET['next']
	else:
		next = '/'

	context = {
		'error': False,
		'next': next
	}

#	if not request.user.is_anonymous():
#s		return HttpResponseRedirect(reverse('home'))

	if request.method == 'POST':
		formulario_acceso = AuthenticationForm(request.POST)
		if formulario_acceso.is_valid:
			email = request.POST['email']
			password = request.POST['password']
			account = authenticate(email=email, password=password)
			#account = authenticate(username=email, password=password)
			if account is not None:
				if account.is_active:
					auth_login(request, account)
					return HttpResponseRedirect(next)
				else:
					context = {
						'status': 'Unauthorized',
						'message': 'Esta cuenta ha sido deshabilidatada.',
						'error': True,
						'next': next
					}
			else:
				context = {
					'status': 'Unauthorized',
					'message': 'email/password combinación inválida.',
					'error': True,
					'next': next
				}
		else:
			pass
	return render(request, 'login.html', context)


@login_required()
def logout(request):
	auth_logout(request)
	return HttpResponseRedirect(reverse('home'))