from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('ayuda/', views.ayuda),
]