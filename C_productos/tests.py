
from django.test import TestCase
from django.core.exceptions import ValidationError

from C_productos.models import Producto
from D_movimientos.models import Movimiento
from D_movimientos.services.movimientos import registrar_movimiento


class MovimientoStockTests(TestCase):

    def setUp(self):
        """
        Prepara un producto con 10 unidades.
        Django usa una base de datos temporal para estas pruebas.
        No modifica los datos reales del sistema.
        """

        self.producto = Producto.objects.create(
            codigo='TEST001',
            nombre='Producto de prueba',
            descripcion='Producto para pruebas automáticas',
            precio='1000.00',
            stock_minimo=2,
            activo=True,
        )

        Movimiento.objects.create(
            producto=self.producto,
            tipo='entrada',
            cantidad=10,
            motivo='Ingreso inicial para pruebas',
        )

    def test_permite_una_salida_valida(self):
        """Permite retirar unidades si hay stock suficiente."""

        registrar_movimiento(
            producto_id=self.producto.pk,
            tipo='salida',
            cantidad=4,
            motivo='Venta de prueba',
        )

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, 6)

    def test_rechaza_una_salida_superior_al_stock(self):
        """Rechaza retirar más unidades de las disponibles."""

        with self.assertRaises(ValidationError):
            registrar_movimiento(
                producto_id=self.producto.pk,
                tipo='salida',
                cantidad=11,
                motivo='Salida que debe rechazarse',
            )

        self.assertEqual(self.producto.stock_actual, 10)

    def test_rechaza_una_cantidad_cero(self):
        """Rechaza cantidades inferiores al mínimo permitido."""

        with self.assertRaises(ValidationError):
            registrar_movimiento(
                producto_id=self.producto.pk,
                tipo='salida',
                cantidad=0,
                motivo='Prueba de cantidad cero',
            )

        self.assertEqual(self.producto.stock_actual, 10)

    def test_rechaza_un_motivo_vacio(self):
        """Rechaza movimientos sin motivo."""

        with self.assertRaises(ValidationError):
            registrar_movimiento(
                producto_id=self.producto.pk,
                tipo='entrada',
                cantidad=5,
                motivo='   ',
            )

        self.assertEqual(self.producto.stock_actual, 10)

    def test_save_directo_rechaza_una_salida_excesiva(self):
        """Comprueba que el modelo rechace una salida excesiva."""

        movimiento = Movimiento(
            producto=self.producto,
            tipo='salida',
            cantidad=11,
            motivo='Prueba de salida excesiva',
        )

        with self.assertRaises(ValidationError):
            movimiento.save()

        self.assertEqual(self.producto.stock_actual, 10)

        self.assertEqual(
            Movimiento.objects.filter(
                producto=self.producto,
                tipo='salida',
            ).count(),
            0,
        )
