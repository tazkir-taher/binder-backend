from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Dater

@admin.register(Dater)
class DaterAdmin(UserAdmin):
    model = Dater
    list_display = ('id','username', 'email', 'first_name', 'last_name', 'gender', 'birth_date','is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {'fields': ('gender', 'birth_date')}),
    )
