from django.contrib.auth.decorators import login_required
from authentication.views import * 

from django.contrib.auth import views as auth_views
from django.urls import path

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


    #path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset_form.html'), name='password_reset'),

    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]