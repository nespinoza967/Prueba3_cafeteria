from django.contrib import admin

from .models import Categoria, DetallePedido, Pedido, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa")
    list_filter = ("activa",)
    search_fields = ("nombre", "descripcion")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "categoria", "precio", "stock", "disponible", "creado")
    list_filter = ("categoria", "disponible")
    search_fields = ("codigo", "nombre")
    list_editable = ("stock", "disponible")


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ("subtotal",)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "fecha", "hora_retiro", "estado", "total")
    list_filter = ("estado", "fecha")
    search_fields = ("cliente__username", "cliente__first_name", "observacion")
    date_hierarchy = "fecha"
    inlines = [DetallePedidoInline]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "producto", "cantidad", "precio_unitario", "subtotal")
    list_filter = ("producto__categoria",)
    search_fields = ("producto__nombre", "producto__codigo")
