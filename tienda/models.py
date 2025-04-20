from django.db import models

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

    # Representación en texto del coche
    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.año})"