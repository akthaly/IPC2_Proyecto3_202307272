from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('visualizarXML/', views.visualizarXML, name='visualizarXML'),
    path('subirXML/', views.subirXML, name='subirXML'),
    path('reset/', views.reset, name='reset'),
    path('resultadoXML/', views.mostrarResultadosXML, name='resultadoXML'),
    path('ayuda/', views.ayuda, name='ayuda'),
]