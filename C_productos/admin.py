
from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'precio',
        'stock_minimo',
        'stock_actual',
        'activo',
    )

    search_fields = ('codigo', 'nombre')
    list_filter = ('activo',)
    ordering = ('nombre',)
    list_per_page = 25
