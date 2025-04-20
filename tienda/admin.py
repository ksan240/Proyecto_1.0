from django.contrib import admin

# Para ver los coches desde el panel admin

from .models import Coche

@admin.register(Coche)
class CocheAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'año', 'precio', 'pais')