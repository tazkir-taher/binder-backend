from django.contrib import admin
from .models import Connection
@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'matched')
    search_fields = ('sender__first_name', 'receiver__first_name')
    list_filter = ('matched',)