from django.contrib import admin

# Para ver los coches desde el panel admin

from .models import Coche, Carrito

@admin.register(Coche)
class CocheAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'año', 'precio', 'pais', 'cantidad_disponible')

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('user', 'coche', 'cantidad')