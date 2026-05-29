from django.urls import path
from . import views

app_name = 'tableros'

urlpatterns = [
    # Inicio y tareas
    path('', views.inicio, name='inicio'),
    path('mis-tareas/', views.mis_tareas, name='mis_tareas'),

    # CRUD Tableros
    path('tablero/crear/', views.crear_tablero, name='crear_tablero'),
    path('tablero/<int:tablero_id>/', views.detalle_tablero, name='detalle_tablero'),
    path('tablero/<int:tablero_id>/editar/', views.editar_tablero, name='editar_tablero'),
    path('tablero/<int:tablero_id>/eliminar/', views.eliminar_tablero, name='eliminar_tablero'),

    # CRUD Listas
    path('tablero/<int:tablero_id>/lista/crear/', views.crear_lista, name='crear_lista'),
    path('lista/<int:lista_id>/eliminar/', views.eliminar_lista, name='eliminar_lista'),

    # CRUD Tarjetas
    path('lista/<int:lista_id>/tarjeta/crear/', views.crear_tarjeta, name='crear_tarjeta'),
    path('tarjeta/<int:tarjeta_id>/editar/', views.editar_tarjeta, name='editar_tarjeta'),
    path('tarjeta/<int:tarjeta_id>/eliminar/', views.eliminar_tarjeta, name='eliminar_tarjeta'),
    path('tarjeta/<int:tarjeta_id>/asignar/', views.asignar_tarjeta, name='asignar_tarjeta'),

    path('tarjeta/<int:tarjeta_id>/estado/', views.cambiar_estado_tarjeta, name='cambiar_estado_tarjeta'),

    path('registro/', views.registro, name='registro'),

    path('actualizar-posicion/', views.actualizar_posicion, name='actualizar_posicion'),
]