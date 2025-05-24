from django.contrib import admin

# Para ver los coches desde el panel admin

from .models import Coche, Carrito, Comentario

@admin.register(Coche)
class CocheAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'año', 'precio', 'pais', 'cantidad_disponible')

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('user', 'coche', 'cantidad')

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('coche', 'usuario', 'valoracion', 'fecha')