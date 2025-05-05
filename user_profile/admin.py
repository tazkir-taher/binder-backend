from django.contrib import admin
from .models import (
    Profile, InterestCategory, UserInterest,
    ProfileQuality, UserQuality, HopingFor
)

class UserInterestInline(admin.TabularInline):
    model = UserInterest
    extra = 1

class UserQualityInline(admin.TabularInline):
    model = UserQuality
    extra = 1

class HopingForInline(admin.TabularInline):
    model = HopingFor
    extra = 1

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'gender', 'location', 'relationship_goal')
    list_filter = ('gender', 'lifestyle', 'relationship_goal')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': (
            'email', 'bio', 'birth_date', 'gender', 'location',
            'lifestyle', 'height', 'relationship_goal'
        )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    inlines = [UserInterestInline, UserQualityInline, HopingForInline]

@admin.register(InterestCategory)
class InterestCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('category', 'name')

@admin.register(ProfileQuality)
class ProfileQualityAdmin(admin.ModelAdmin):
    list_display = ('name', 'choice')
    list_filter = ('choice',)
    search_fields = ('name',)