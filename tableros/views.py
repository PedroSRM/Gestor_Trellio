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


@login_required
def asignar_tarjeta(request, tarjeta_id):
    """
    Solo el Admin puede asignar tarjetas a otros usuarios.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        if usuario_id:
            usuario = get_object_or_404(User, id=usuario_id)
            tarjeta.asignado_a = usuario
            tarjeta.save()
        return redirect('tableros:detalle_tablero', tablero_id=tarjeta.lista.tablero.id)

    # Solo usuarios normales aparecen en la lista de asignación
    usuarios_normales = User.objects.filter(is_superuser=False)
    return render(request, 'tableros/asignar_tarjeta.html', {
        'tarjeta': tarjeta,
        'usuarios_normales': usuarios_normales
    })


@login_required
def mis_tareas(request):
    """
    Vista exclusiva del Usuario Normal:
    muestra únicamente las tarjetas que le fueron asignadas.
    """
    if request.user.is_superuser:
        return redirect('tableros:inicio')

    tarjetas_asignadas = Tarjeta.objects.filter(
        asignado_a=request.user
    ).select_related('lista__tablero')

    return render(request, 'tableros/mis_tareas.html', {
        'tarjetas_asignadas': tarjetas_asignadas
    })