from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile, Interest, UserInterest

class UserInterestInline(admin.TabularInline):
    model = UserInterest
    extra = 1

@admin.register(Profile)
class ProfileAdmin(UserAdmin):
    list_display = ('username', 'email', 'gender', 'location')
    list_filter = ('gender',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'bio', 'birth_date', 'gender', 'location')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    inlines = [UserInterestInline]

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)