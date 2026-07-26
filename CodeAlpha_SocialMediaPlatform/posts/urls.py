from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('create/', views.create_post, name='create_post'),
    path('stories/create/', views.create_story, name='create_story'),
    path('stories/<int:story_id>/', views.story_detail, name='story_detail'),
    path('stories/<int:story_id>/like/', views.like_story, name='like_story'),
    path('stories/<int:story_id>/delete/', views.delete_story, name='delete_story'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/like/', views.like_post, name='like_post'),
    path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('explore/', views.explore, name='explore'),
]
