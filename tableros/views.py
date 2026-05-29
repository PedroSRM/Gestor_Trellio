from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from .models import Tablero, Lista, Tarjeta

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST


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

# ==================== CRUD TABLEROS ====================

@login_required
def crear_tablero(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        if nombre:
            Tablero.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                creado_por=request.user
            )
        return redirect('tableros:inicio')
    return render(request, 'tableros/crear_tablero.html')


@login_required
def editar_tablero(request, tablero_id):
    if request.user.is_superuser:
        tablero = get_object_or_404(Tablero, id=tablero_id)
    else:
        tablero = get_object_or_404(Tablero, id=tablero_id, creado_por=request.user)

    if request.method == 'POST':
        tablero.nombre = request.POST.get('nombre', tablero.nombre)
        tablero.descripcion = request.POST.get('descripcion', tablero.descripcion)
        tablero.save()
        return redirect('tableros:detalle_tablero', tablero_id=tablero.id)
    return render(request, 'tableros/editar_tablero.html', {'tablero': tablero})


@login_required
def eliminar_tablero(request, tablero_id):
    if request.user.is_superuser:
        tablero = get_object_or_404(Tablero, id=tablero_id)
    else:
        tablero = get_object_or_404(Tablero, id=tablero_id, creado_por=request.user)

    if request.method == 'POST':
        tablero.delete()
        return redirect('tableros:inicio')
    return render(request, 'tableros/eliminar_tablero.html', {'tablero': tablero})


# ==================== CRUD LISTAS ====================

@login_required
def crear_lista(request, tablero_id):
    if request.user.is_superuser:
        tablero = get_object_or_404(Tablero, id=tablero_id)
    else:
        tablero = get_object_or_404(Tablero, id=tablero_id, creado_por=request.user)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            posicion = tablero.listas.count()
            Lista.objects.create(nombre=nombre, tablero=tablero, posicion=posicion)
        return redirect('tableros:detalle_tablero', tablero_id=tablero.id)
    return render(request, 'tableros/crear_lista.html', {'tablero': tablero})


@login_required
def eliminar_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)
    tablero_id = lista.tablero.id

    if not request.user.is_superuser and lista.tablero.creado_por != request.user:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    if request.method == 'POST':
        lista.delete()
    return redirect('tableros:detalle_tablero', tablero_id=tablero_id)


# ==================== CRUD TARJETAS ====================

@login_required
def crear_tarjeta(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)

    if not request.user.is_superuser and lista.tablero.creado_por != request.user:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion', '')
        if titulo:
            posicion = lista.tarjetas.count()
            Tarjeta.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                lista=lista,
                posicion=posicion
            )
        return redirect('tableros:detalle_tablero', tablero_id=lista.tablero.id)
    return render(request, 'tableros/crear_tarjeta.html', {'lista': lista})


@login_required
def editar_tarjeta(request, tarjeta_id):
    tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)

    if not request.user.is_superuser and tarjeta.lista.tablero.creado_por != request.user:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    if request.method == 'POST':
        tarjeta.titulo = request.POST.get('titulo', tarjeta.titulo)
        tarjeta.descripcion = request.POST.get('descripcion', tarjeta.descripcion)
        tarjeta.save()
        return redirect('tableros:detalle_tablero', tablero_id=tarjeta.lista.tablero.id)
    return render(request, 'tableros/editar_tarjeta.html', {'tarjeta': tarjeta})


@login_required
def eliminar_tarjeta(request, tarjeta_id):
    tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)
    tablero_id = tarjeta.lista.tablero.id

    if not request.user.is_superuser and tarjeta.lista.tablero.creado_por != request.user:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    if request.method == 'POST':
        tarjeta.delete()
    return redirect('tableros:detalle_tablero', tablero_id=tablero_id)

@login_required
def cambiar_estado_tarjeta(request, tarjeta_id):
    tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)

    if not request.user.is_superuser and tarjeta.asignado_a != request.user:
        return HttpResponseForbidden("No tienes permiso para realizar esta acción.")

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in ['por_hacer', 'en_progreso', 'terminado']:
            tarjeta.estado = nuevo_estado
            tarjeta.save()
    return redirect('tableros:detalle_tablero', tablero_id=tarjeta.lista.tablero.id)

def registro(request):
    if request.user.is_authenticated:
        return redirect('tableros:inicio')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('tableros:inicio')
    else:
        form = UserCreationForm()
    return render(request, 'auth/registro.html', {'form': form})

@login_required
@require_POST
def actualizar_posicion(request):
    try:
        data = json.loads(request.body)
        tarjetas = data.get('tarjetas', [])
        for item in tarjetas:
            Tarjeta.objects.filter(id=item['id']).update(
                posicion=item['posicion'],
                lista_id=item['lista_id']
            )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)