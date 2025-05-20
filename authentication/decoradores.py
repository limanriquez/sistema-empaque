from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def require_personal(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'personal') and request.user.personal:
            return view_func(request, *args, **kwargs)
        else:
            if request.user.is_superuser or request.user.is_staff:
                messages.error(request, "No tienes un registro de personal asociado a tu usuario. Como administrador asigna uno para continuar")
                return redirect('/admin/')
            else:
                messages.error(request, "No tienes un registro de personal asociado a tu usuario. Contacta con el administrador.")
                return redirect('logout')
    return _wrapped_view