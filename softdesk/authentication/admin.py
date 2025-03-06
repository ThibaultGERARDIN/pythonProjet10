from django.contrib import admin
from .models import MyUser
from django.contrib.auth.admin import UserAdmin


@admin.register(MyUser)
class CustomUserAdmin(UserAdmin):
    readonly_fields = [
        "can_be_contacted",
        "can_data_be_shared",
    ]
