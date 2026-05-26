from django.urls import path
from . import views

app_name = 'tableros'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('tablero/<int:tablero_id>/', views.detalle_tablero, name='detalle_tablero'),
]