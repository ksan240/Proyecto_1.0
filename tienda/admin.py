from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Para ver los coches desde el panel admin

from .models import Coche, Carrito, Comentario, Venta

@admin.register(Coche)
class CocheAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'año', 'precio', 'pais', 'cantidad_disponible')

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('user', 'coche', 'cantidad')

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('coche', 'usuario', 'valoracion', 'fecha')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'coche', 'cantidad', 'fecha')

# Para añadir el correo a users

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )