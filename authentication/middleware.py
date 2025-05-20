from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse, NoReverseMatch

class CheckUserHasPersonalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and not user.is_superuser:
            # Si el usuario no tiene el atributo 'personal' o es None:
            if not hasattr(user, 'personal') or user.personal is None:
                logout(request)            # Lo desloguea
                return redirect('/login/') # Lo manda a login (ajusta la URL si es otra)
        return self.get_response(request)