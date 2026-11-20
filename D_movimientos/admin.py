
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Movimiento
from .forms import MovimientoAdminForm
from .services.movimientos import registrar_movimiento


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):

    form = MovimientoAdminForm

    list_display = (
        'producto',
        'tipo',
        'cantidad',
        'motivo',
        'fecha',
        'usuario',
    )

    list_filter = ('tipo', 'fecha')

    search_fields = (
        'producto__nombre',
        'producto__codigo',
        'motivo',
    )

    readonly_fields = ('fecha',)

    def has_change_permission(self, request, obj=None):
        # Permite crear movimientos, pero no editar los existentes.
        if obj is not None:
            return False

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # No permite eliminar movimientos del historial.
        return False

    def save_model(self, request, obj, form, change):
        # No permitimos modificar movimientos existentes.
        if change:
            raise ValidationError(
                'Los movimientos existentes no se pueden modificar.'
            )

        # Registramos el movimiento mediante el servicio centralizado.
        movimiento = registrar_movimiento(
            producto_id=obj.producto_id,
            tipo=obj.tipo,
            cantidad=obj.cantidad,
            motivo=obj.motivo,
            usuario=request.user,
        )

        # Conservamos el identificador y la fecha del registro creado.
        obj.pk = movimiento.pk
        obj.fecha = movimiento.fecha
        obj._state.adding = False
        obj._state.db = movimiento._state.db
