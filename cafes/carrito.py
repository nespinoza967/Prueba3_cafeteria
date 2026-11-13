from django.db import transaction

from .models import DetallePedido, Pedido, Producto

SESSION_KEY = "carrito"
MAX_UNIDADES = 10


class StockInsuficiente(Exception):
    pass


class Carrito:
    """Carrito guardado en la sesión como {"id_producto": cantidad}."""

    def __init__(self, request):
        self.session = request.session
        self.items = self.session.get(SESSION_KEY, {})

    def guardar(self):
        self.session[SESSION_KEY] = self.items
        self.session.modified = True

    def cantidad(self, producto_id):
        return self.items.get(str(producto_id), 0)

    def unidades(self):
        return sum(self.items.values())

    def fijar(self, producto, cantidad):
        """Deja `cantidad` unidades del producto. Devuelve un mensaje de error o None."""
        if cantidad <= 0:
            self.quitar(producto.pk)
            return None
        if cantidad > producto.stock:
            return f'Solo hay {producto.stock} unidades disponibles de "{producto.nombre}".'
        otras = self.unidades() - self.cantidad(producto.pk)
        if otras + cantidad > MAX_UNIDADES:
            return f"Un pedido no puede tener más de {MAX_UNIDADES} unidades en total."
        self.items[str(producto.pk)] = cantidad
        self.guardar()
        return None

    def quitar(self, producto_id):
        self.items.pop(str(producto_id), None)
        self.guardar()

    def vaciar(self):
        self.items = {}
        self.guardar()

    def lineas(self):
        """Productos del carrito con su cantidad y subtotal al precio vigente."""
        productos = Producto.objects.filter(pk__in=self.items.keys()).select_related("categoria")
        lineas = [
            {"producto": p, "cantidad": self.items[str(p.pk)], "subtotal": p.precio * self.items[str(p.pk)]}
            for p in productos
        ]
        if len(lineas) != len(self.items):
            self.items = {str(l["producto"].pk): l["cantidad"] for l in lineas}
            self.guardar()
        return lineas


def crear_pedido(cliente, carrito, hora_retiro, observacion):
    """Crea el pedido completo o nada. Lanza StockInsuficiente indicando qué productos fallaron."""
    with transaction.atomic():
        productos = Producto.objects.select_for_update().in_bulk(
            [int(pk) for pk in carrito.items]
        )
        faltantes = []
        for pk, cantidad in carrito.items.items():
            producto = productos.get(int(pk))
            if producto is None:
                faltantes.append("un producto que ya no existe")
            elif not producto.disponible or producto.stock < cantidad:
                faltantes.append(f'"{producto.nombre}" (stock: {producto.stock})')
        if faltantes:
            raise StockInsuficiente(
                "No se pudo confirmar el pedido. Sin stock suficiente: " + ", ".join(faltantes) + "."
            )

        pedido = Pedido.objects.create(
            cliente=cliente,
            hora_retiro=hora_retiro,
            observacion=observacion,
            estado=Pedido.PENDIENTE,
        )
        total = 0
        for pk, cantidad in carrito.items.items():
            producto = productos[int(pk)]
            subtotal = producto.precio * cantidad
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=subtotal,
            )
            producto.stock -= cantidad
            producto.save(update_fields=["stock"])
            total += subtotal
        pedido.total = total
        pedido.save(update_fields=["total"])
    return pedido