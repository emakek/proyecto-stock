from django.db import models
from django.db.models import Sum, Q


class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    @property
    def stock_actual(self):
        movimientos = self.movimiento_set.aggregate(
            entradas=Sum('cantidad', filter=Q(tipo='entrada')),
            salidas=Sum('cantidad', filter=Q(tipo='salida')),
        )

        entradas = movimientos['entradas'] or 0
        salidas = movimientos['salidas'] or 0

        return entradas - salidas