from django.db import models

from django.contrib.auth.models import User

class Coche(models.Model):
    # Opciones para las marcas de coches
    OPCIONES_MARCA = [
        ('Ferrari', 'Ferrari'),
        ('Lamborghini', 'Lamborghini'),
        ('Pagani', 'Pagani'),
        ('McLaren', 'McLaren'),
        ('BMW', 'BMW'),
    ]

    # Campos del modelo
    marca = models.CharField(max_length=50, choices=OPCIONES_MARCA)  # Marca del coche
    modelo = models.CharField(max_length=100)  # Modelo del coche
    año = models.IntegerField()  # Año de fabricación
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio del coche
    pais = models.CharField(max_length=100)  # País de origen
    descripcion = models.TextField(blank=True, null=True)  # Descripción del coche
    imagen = models.ImageField(upload_to='coches/', blank=True, null=True)  # Imagen del coche
    cantidad_disponible = models.PositiveIntegerField(default=0)  # Cantidad disponible

    # Representación en texto del coche
    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.año})"
    

class Carrito(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coche = models.ForeignKey(Coche, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.coche.marca} {self.coche.modelo} - {self.cantidad}"

class Comentario(models.Model):
    coche = models.ForeignKey(Coche, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    valoracion = models.PositiveSmallIntegerField(default=5)  # 1 a 5 estrellas
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.valoracion}⭐"