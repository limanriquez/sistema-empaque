from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required()
def home(request):
	return render(request, 'home.html')


def error_404(request, exception):
        return render(request, '404.html', status=404)


def error_500(request):
        return render(request, '500.html', status=500)