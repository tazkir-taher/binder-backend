from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'