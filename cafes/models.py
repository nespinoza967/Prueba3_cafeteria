from django.conf import settings
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="productos"
    )
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    precio = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Pedido(models.Model):
    PENDIENTE = "PENDIENTE"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO = "LISTO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"
    ESTADOS = [
        (PENDIENTE, "Pendiente"),
        (EN_PREPARACION, "En preparación"),
        (LISTO, "Listo"),
        (ENTREGADO, "Entregado"),
        (CANCELADO, "Cancelado"),
    ]

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pedidos"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    hora_retiro = models.TimeField()
    estado = models.CharField(max_length=15, choices=ESTADOS, default=PENDIENTE)
    total = models.PositiveIntegerField(default=0)
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente.username} ({self.get_estado_display()})"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name="detalles"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="detalles"
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    class Meta:
        verbose_name = "detalle de pedido"
        verbose_name_plural = "detalles de pedido"
        constraints = [
            models.UniqueConstraint(
                fields=["pedido", "producto"], name="unico_producto_por_pedido"
            )
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
