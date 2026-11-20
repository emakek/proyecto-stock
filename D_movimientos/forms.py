
from django import forms
from django.core.exceptions import ValidationError

from .models import Movimiento


class MovimientoAdminForm(forms.ModelForm):

    class Meta:
        model = Movimiento
        fields = '__all__'

    def clean(self):
        datos = super().clean()

        producto = datos.get('producto')
        tipo = datos.get('tipo')
        cantidad = datos.get('cantidad')

        # Solo comprobamos el stock cuando es una salida.
        if (
            producto is not None
            and tipo == 'salida'
            and cantidad is not None
        ):
            stock_disponible = producto.stock_actual

            if cantidad > stock_disponible:
                self.add_error(
                    'cantidad',
                    (
                        f'Stock insuficiente. '
                        f'Stock disponible: {stock_disponible}.'
                    )
                )

        return datos
