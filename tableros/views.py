from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from .models import Tablero, Lista, Tarjeta


def get_tableros_para_usuario(usuario):
    """
    Regla central de permisos:
    - Admin (superusuario): ve todos los tableros de la plataforma.
    - Usuario Normal: solo ve los tableros que él creó.
    """
    if usuario.is_superuser:
        return Tablero.objects.all()
    return Tablero.objects.filter(creado_por=usuario)


@login_required
def inicio(request):
    tableros = get_tableros_para_usuario(request.user)
    return render(request, 'tableros/inicio.html', {
        'tableros': tableros,
        'es_admin': request.user.is_superuser
    })


@login_required
def detalle_tablero(request, tablero_id):
    if request.user.is_superuser:
        tablero = get_object_or_404(Tablero, id=tablero_id)
    else:
        tablero = get_object_or_404(Tablero, id=tablero_id, creado_por=request.user)

    listas = tablero.listas.all()
    return render(request, 'tableros/detalle_tablero.html', {
        'tablero': tablero,
        'listas': listas,
        'es_admin': request.user.is_superuser
    })