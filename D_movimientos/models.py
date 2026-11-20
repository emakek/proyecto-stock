
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q


class Movimiento(models.Model):

    TIPOS = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]

    producto = models.ForeignKey(
        'C_productos.Producto',
        on_delete=models.PROTECT
    )

    tipo = models.CharField(
        max_length=10,
        choices=TIPOS
    )

    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    motivo = models.CharField(max_length=200)

    fecha = models.DateTimeField(auto_now_add=True)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.producto} - {self.tipo} - {self.cantidad}"

    def clean(self):
        super().clean()

        # Si todavía faltan datos, dejamos que Django
        # informe los errores de validación correspondientes.
        if (
            self.tipo != 'salida'
            or not self.producto_id
            or self.cantidad is None
        ):
            return

        # Calculamos las entradas y salidas registradas.
        movimientos = self.producto.movimiento_set.aggregate(
            entradas=Sum(
                'cantidad',
                filter=Q(tipo='entrada')
            ),
            salidas=Sum(
                'cantidad',
                filter=Q(tipo='salida')
            ),
        )

        entradas = movimientos['entradas'] or 0
        salidas = movimientos['salidas'] or 0

        stock_disponible = entradas - salidas

        # Si estamos validando un movimiento existente,
        # recuperamos su cantidad anterior cuando corresponde.
        if self.pk:
            movimiento_anterior = (
                Movimiento.objects
                .filter(pk=self.pk)
                .first()
            )

            if (
                movimiento_anterior is not None
                and movimiento_anterior.tipo == 'salida'
            ):
                stock_disponible += movimiento_anterior.cantidad

        # Rechazamos una salida que supere el stock.
        if self.cantidad > stock_disponible:
            raise ValidationError({
                'cantidad': (
                    f'Stock insuficiente. '
                    f'Stock disponible: {stock_disponible}.'
                )
            })

    def save(self, *args, **kwargs):
        # Ejecutamos las validaciones antes de guardar.
        self.full_clean()

        # Guardamos solamente si las validaciones pasan.
        super().save(*args, **kwargs)
