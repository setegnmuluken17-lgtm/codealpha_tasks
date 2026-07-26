from django.urls import path

from . import views


urlpatterns = [
    path('', views.inbox, name='chat_inbox'),
    path('<str:username>/', views.thread, name='chat_thread'),
]
