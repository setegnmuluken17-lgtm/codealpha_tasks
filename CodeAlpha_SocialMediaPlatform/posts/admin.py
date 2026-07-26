from django.contrib import admin
from .models import Post, Like, Comment, Story, StoryLike, StoryView


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_preview', 'created_at', 'like_count', 'comment_count')
    list_filter = ('created_at', 'author')
    search_fields = ('author__username', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Post Information', {
            'fields': ('author', 'content', 'image', 'video')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__author__username')
    readonly_fields = ('created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'content_preview')
    list_filter = ('created_at', 'author')
    search_fields = ('author__username', 'post__author__username', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Comment Information', {
            'fields': ('post', 'author', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('author', 'caption_preview', 'created_at', 'expires_at', 'is_active')
    list_filter = ('created_at', 'expires_at', 'author')
    search_fields = ('author__username', 'caption')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Story Information', {
            'fields': ('author', 'caption', 'image', 'video')
        }),
        ('Availability', {
            'fields': ('created_at', 'expires_at')
        }),
    )

    def caption_preview(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = 'Caption'


@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ('story', 'user', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('story__author__username', 'user__username')
    readonly_fields = ('viewed_at',)


@admin.register(StoryLike)
class StoryLikeAdmin(admin.ModelAdmin):
    list_display = ('story', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('story__author__username', 'user__username')
    readonly_fields = ('created_at',)
