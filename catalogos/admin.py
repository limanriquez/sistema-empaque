from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import GoHome


@admin.register(GoHome)
class GoHomeAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_model_perms(self, request):
        return {
            "add": False,
            "change": True,
            "delete": False,
            "view": False,
        }

    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("home"))
