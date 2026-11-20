
from django.core.exceptions import ValidationError
from django.db import transaction

from C_productos.models import Producto
from D_movimientos.models import Movimiento


@transaction.atomic
def registrar_movimiento(
    *,
    producto_id,
    tipo,
    cantidad,
    motivo,
    usuario=None,
):
    """
    Registra una entrada o salida de stock de forma controlada.
    """

    # Validamos el tipo de movimiento.
    if tipo not in ('entrada', 'salida'):
        raise ValidationError(
            'El tipo de movimiento no es válido.'
        )

    # Validamos la cantidad.
    if (
        not isinstance(cantidad, int)
        or isinstance(cantidad, bool)
        or cantidad < 1
    ):
        raise ValidationError(
            'La cantidad debe ser un entero mayor que cero.'
        )

    # Validamos el motivo.
    if not motivo or not motivo.strip():
        raise ValidationError(
            'El motivo es obligatorio.'
        )

    # Recuperamos el producto dentro de la transacción.
    producto = (
        Producto.objects
        .select_for_update()
        .get(pk=producto_id)
    )

    # Comprobamos que haya stock suficiente para una salida.
    if tipo == 'salida':
        stock_disponible = producto.stock_actual

        if cantidad > stock_disponible:
            raise ValidationError(
                f'Stock insuficiente. '
                f'Stock disponible: {stock_disponible}.'
            )

    # Preparamos el movimiento.
    movimiento = Movimiento(
        producto=producto,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo.strip(),
        usuario=usuario,
    )

    # save() ejecuta full_clean() automáticamente.
    movimiento.save()

    return movimiento
