from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create-room/', views.create_room, name='create_room'),
    path('join-room/', views.join_room, name='join_room'),
    path('room/<uuid:room_id>/', views.room_view, name='room'),
]