from django.contrib.auth.decorators import login_required
from authentication.views import * 

from django.urls import path, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

#router.register(r'accounts', AccountViewSet)
#router.register(r'companies', CompanyViewSet)
#router.register('personas',PersonasViewSet)
app_name = 'authentication'
urlpatterns = [
    path('api/v1/',include(router.urls)),
    path('login/', login, name="login"),
    path('logout/', logout, name='logout'),
]