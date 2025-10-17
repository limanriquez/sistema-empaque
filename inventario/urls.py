"""inventarios URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from inventario.views import home, error_404, error_500

handler404 = error_404
handler500 = error_500
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
  #  path('',include('personas.urls')),
    path('',include('operaciones.urls',namespace='operaciones')),
    path('',include('servicios.urls',namespace='servicios')),
    path('',include('inventarios.urls',namespace='inventarios')),
    path('',include('usuarios.urls',namespace='usuarios')),
    path('',include('empresa.urls',namespace='empresa')),
    path('',include('catalogos.urls',namespace='catalogos')),
  #  path('',include('users.urls',namespace='users')),
    path('user/', include('users.urls', namespace='user')),  # Usa 'users' si la app se llama así
    path('',include('authentication.urls',namespace='authentication')),
]
