from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='visualizarXML'),
    path('ayuda/', views.ayuda, name='ayuda'),
]