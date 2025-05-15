from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Dater

@admin.register(Dater)
class DaterAdmin(UserAdmin):

    list_display = ('email', 'first_name', 'last_name', 'gender', 'is_staff', 'is_active')

    search_fields = ('email', 'first_name', 'last_name')

    ordering = ('email',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'birth_date', 'gender')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'birth_date', 'gender', 'password1', 'password2'),
        }),
    )
