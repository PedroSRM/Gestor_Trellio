from django.contrib import admin
from .models import Tablero, Lista, Tarjeta
from .models import Tablero, Lista, Tarjeta, Notificacion

@admin.register(Tablero)
class TableroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'creado_por', 'fecha_creacion']
    list_filter = ['creado_por']


@admin.register(Lista)
class ListaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tablero', 'posicion']


@admin.register(Tarjeta)
class TarjetaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'lista', 'asignado_a', 'posicion']
    list_filter = ['asignado_a']

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'mensaje', 'leida', 'fecha']