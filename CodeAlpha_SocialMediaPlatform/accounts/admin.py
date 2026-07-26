from django.contrib import admin
from .models import UserProfile, Follow


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'joined_date')
    list_filter = ('joined_date',)
    search_fields = ('user__username', 'user__email', 'location')
    readonly_fields = ('joined_date', 'updated_date')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('bio', 'profile_picture', 'cover_photo', 'location', 'website', 'birth_date')
        }),
        ('Timestamps', {
            'fields': ('joined_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    readonly_fields = ('created_at',)
