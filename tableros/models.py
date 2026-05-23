from django.db import models
from django.contrib.auth.models import User


class Tablero(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tableros'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Lista(models.Model):
    nombre = models.CharField(max_length=200)
    tablero = models.ForeignKey(
        Tablero,
        on_delete=models.CASCADE,
        related_name='listas'
    )
    posicion = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['posicion']

    def __str__(self):
        return f"{self.nombre} — {self.tablero.nombre}"


class Tarjeta(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    lista = models.ForeignKey(
        Lista,
        on_delete=models.CASCADE,
        related_name='tarjetas'
    )
    asignado_a = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tarjetas_asignadas'
    )
    posicion = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['posicion']

    def __str__(self):
        return self.titulo