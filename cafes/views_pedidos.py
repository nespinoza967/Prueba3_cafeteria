"""RF-06: seguimiento de pedidos (cliente y encargado)."""
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .decorators import cliente_required, encargado_required
from .models import Pedido, Producto

# Flujo permitido: cada estado solo puede avanzar al siguiente.
SIGUIENTE_ESTADO = {
    Pedido.PENDIENTE: Pedido.EN_PREPARACION,
    Pedido.EN_PREPARACION: Pedido.LISTO,
    Pedido.LISTO: Pedido.ENTREGADO,
}


# ---------- Cliente ----------

@cliente_required
def mis_pedidos(request):
    pedidos = (
        Pedido.objects.filter(cliente=request.user)
        .prefetch_related("detalles__producto")
    )
    return render(request, "cafes/mis_pedidos.html", {"pedidos": pedidos})


@cliente_required
def pedido_detalle(request, pk):
    # Filtrar por cliente: un pedido ajeno responde 404 aunque se cambie el id en la URL.
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related("detalles__producto"),
        pk=pk, cliente=request.user,
    )
    return render(request, "cafes/pedido_detalle.html", {"pedido": pedido})


@cliente_required
@require_POST
def pedido_cancelar(request, pk):
    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(), pk=pk, cliente=request.user
        )
        if pedido.estado != Pedido.PENDIENTE:
            messages.error(request, f"El pedido #{pedido.pk} ya no se puede cancelar (está {pedido.get_estado_display()}).")
            return redirect("mis_pedidos")

        for detalle in pedido.detalles.all():
            Producto.objects.filter(pk=detalle.producto_id).update(stock=F("stock") + detalle.cantidad)

        pedido.estado = Pedido.CANCELADO
        pedido.save(update_fields=["estado"])

    messages.success(request, f"Pedido #{pedido.pk} cancelado. El stock fue repuesto.")
    return redirect("mis_pedidos")


# ---------- Encargado ----------

@encargado_required
def pedidos_dia(request):
    hoy = timezone.localdate()
    pedidos = (
        Pedido.objects.filter(fecha__date=hoy)
        .select_related("cliente")
        .prefetch_related("detalles__producto")
        .order_by("hora_retiro")
    )

    estado = request.GET.get("estado", "")
    estados_validos = dict(Pedido.ESTADOS)
    if estado in estados_validos:
        pedidos = pedidos.filter(estado=estado)
    else:
        estado = ""

    for p in pedidos:
        sig = SIGUIENTE_ESTADO.get(p.estado)
        p.siguiente_estado = sig
        p.siguiente_estado_display = estados_validos.get(sig, "")

    return render(request, "cafes/pedidos_dia.html", {
        "pedidos": pedidos,
        "estados": Pedido.ESTADOS,
        "estado": estado,
        "hoy": hoy,
    })


@encargado_required
@require_POST
def pedido_avanzar(request, pk):
    # Volver a la misma lista filtrada, solo si es una URL interna del sitio.
    volver = request.POST.get("volver", "")
    if not url_has_allowed_host_and_scheme(volver, allowed_hosts={request.get_host()}):
        volver = "pedidos_dia"
    with transaction.atomic():
        pedido = get_object_or_404(Pedido.objects.select_for_update(), pk=pk)

        # El formulario envía el estado que veía el encargado; si no coincide
        # (doble clic o pestaña desactualizada) no se avanza, para no saltarse estados.
        if request.POST.get("estado_actual") != pedido.estado:
            messages.error(request, f"El pedido #{pedido.pk} cambió de estado; revisa la lista e inténtalo de nuevo.")
            return redirect(volver)

        siguiente = SIGUIENTE_ESTADO.get(pedido.estado)
        if siguiente is None:
            messages.error(request, f"El pedido #{pedido.pk} está {pedido.get_estado_display()} y no puede avanzar.")
            return redirect(volver)

        pedido.estado = siguiente
        pedido.save(update_fields=["estado"])

    messages.success(request, f"Pedido #{pedido.pk} pasó a {pedido.get_estado_display()}.")
    return redirect(volver)
