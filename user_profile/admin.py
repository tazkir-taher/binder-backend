from django.contrib import admin
from .models import DaterProfile

@admin.register(DaterProfile)
class DaterProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'location', 'height')
    search_fields = ('user__email', 'location')
