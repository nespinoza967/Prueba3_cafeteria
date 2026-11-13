from django.contrib import messages
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .carrito import Carrito, StockInsuficiente, crear_pedido
from .decorators import cliente_required, encargado_required
from .forms import CantidadForm, CategoriaForm, ConfirmarPedidoForm, ProductoForm
from .models import Categoria, Producto


def inicio(request):
    """Redirige a la página principal según el rol."""
    if request.user.is_staff:
        return redirect("panel_encargado")
    return redirect("catalogo")


@cliente_required
def catalogo(request):
    categorias = Categoria.objects.filter(activa=True)
    productos = Producto.objects.filter(
        disponible=True, categoria__activa=True
    ).select_related("categoria")

    q = request.GET.get("q", "").strip()
    if q:
        productos = productos.filter(nombre__icontains=q)

    categoria_id = request.GET.get("categoria", "")
    if categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))
    else:
        categoria_id = ""

    return render(request, "cafes/catalogo.html", {
        "productos": productos,
        "categorias": categorias,
        "q": q,
        "categoria_id": categoria_id,
    })


@encargado_required
def panel_encargado(request):
    return render(request, "cafes/panel_encargado.html")


# ---------- Categorías ----------

@encargado_required
def categoria_lista(request):
    categorias = Categoria.objects.annotate(num_productos=Count("productos"))
    return render(request, "cafes/categoria_lista.html", {"categorias": categorias})


@encargado_required
def categoria_detalle(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    return render(request, "cafes/categoria_detalle.html", {
        "categoria": categoria,
        "productos": categoria.productos.all(),
    })


@encargado_required
def categoria_crear(request):
    form = CategoriaForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria}" creada correctamente.')
            return redirect("categoria_detalle", pk=categoria.pk)
        messages.error(request, "No se pudo crear la categoría. Revisa los errores.")
    return render(request, "cafes/form.html", {
        "form": form,
        "titulo": "Nueva categoría",
        "volver": reverse("categoria_lista"),
    })


@encargado_required
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria}" actualizada correctamente.')
            return redirect("categoria_detalle", pk=categoria.pk)
        messages.error(request, "No se pudo guardar la categoría. Revisa los errores.")
    return render(request, "cafes/form.html", {
        "form": form,
        "titulo": f"Editar categoría: {categoria}",
        "volver": reverse("categoria_detalle", args=[pk]),
    })


@encargado_required
def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        try:
            categoria.delete()
        except ProtectedError:
            messages.error(
                request,
                f'No se puede eliminar "{categoria}" porque tiene productos asociados.',
            )
            return redirect("categoria_detalle", pk=pk)
        messages.success(request, f'Categoría "{categoria}" eliminada correctamente.')
        return redirect("categoria_lista")
    return render(request, "cafes/confirmar_eliminar.html", {
        "objeto": categoria,
        "tipo": "la categoría",
        "volver": reverse("categoria_detalle", args=[pk]),
    })


# ---------- Productos ----------

@encargado_required
def producto_lista(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.select_related("categoria")

    q = request.GET.get("q", "").strip()
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))

    categoria_id = request.GET.get("categoria", "")
    if categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))
    else:
        categoria_id = ""

    disponible = request.GET.get("disponible", "")
    if disponible == "si":
        productos = productos.filter(disponible=True)
    elif disponible == "no":
        productos = productos.filter(disponible=False)
    else:
        disponible = ""

    return render(request, "cafes/producto_lista.html", {
        "productos": productos,
        "categorias": categorias,
        "q": q,
        "categoria_id": categoria_id,
        "disponible": disponible,
    })


@encargado_required
def producto_detalle(request, pk):
    producto = get_object_or_404(Producto.objects.select_related("categoria"), pk=pk)
    return render(request, "cafes/producto_detalle.html", {"producto": producto})


@encargado_required
def producto_crear(request):
    form = ProductoForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto}" creado correctamente.')
            return redirect("producto_detalle", pk=producto.pk)
        messages.error(request, "No se pudo crear el producto. Revisa los errores.")
    return render(request, "cafes/form.html", {
        "form": form,
        "titulo": "Nuevo producto",
        "volver": reverse("producto_lista"),
    })


@encargado_required
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto}" actualizado correctamente.')
            return redirect("producto_detalle", pk=producto.pk)
        messages.error(request, "No se pudo guardar el producto. Revisa los errores.")
    return render(request, "cafes/form.html", {
        "form": form,
        "titulo": f"Editar producto: {producto}",
        "volver": reverse("producto_detalle", args=[pk]),
    })


@encargado_required
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        try:
            producto.delete()
        except ProtectedError:
            messages.error(
                request,
                f'No se puede eliminar "{producto}" porque ya forma parte de pedidos. '
                "Puedes marcarlo como no disponible.",
            )
            return redirect("producto_detalle", pk=pk)
        messages.success(request, f'Producto "{producto}" eliminado correctamente.')
        return redirect("producto_lista")
    return render(request, "cafes/confirmar_eliminar.html", {
        "objeto": producto,
        "tipo": "el producto",
        "volver": reverse("producto_detalle", args=[pk]),
    })



# carito

@cliente_required
def carrito_ver(request):
    carrito = Carrito(request)
    lineas = carrito.lineas()
    return render(request, "cafes/carrito.html", {
        "lineas": lineas,
        "total": sum(l["subtotal"] for l in lineas),
        "unidades": carrito.unidades(),
    })


@cliente_required
@require_POST
def carrito_agregar(request, pk):
    producto = get_object_or_404(Producto, pk=pk, disponible=True, categoria__activa=True)
    form = CantidadForm(request.POST)
    if not form.is_valid():
        messages.error(request, "La cantidad indicada no es válida.")
        return redirect("catalogo")
    carrito = Carrito(request)
    error = carrito.fijar(producto, carrito.cantidad(pk) + form.cleaned_data["cantidad"])
    if error:
        messages.error(request, error)
    else:
        messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    return redirect("catalogo")


@cliente_required
@require_POST
def carrito_actualizar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = CantidadForm(request.POST)
    if not form.is_valid():
        messages.error(request, "La cantidad indicada no es válida.")
        return redirect("carrito")
    error = Carrito(request).fijar(producto, form.cleaned_data["cantidad"])
    if error:
        messages.error(request, error)
    else:
        messages.success(request, f'Cantidad de "{producto.nombre}" actualizada.')
    return redirect("carrito")


@cliente_required
@require_POST
def carrito_quitar(request, pk):
    Carrito(request).quitar(pk)
    messages.success(request, "Producto quitado del carrito.")
    return redirect("carrito")


@cliente_required
@require_POST
def carrito_vaciar(request):
    Carrito(request).vaciar()
    messages.success(request, "Carrito vaciado.")
    return redirect("carrito")


@cliente_required
def pedido_confirmar(request):
    carrito = Carrito(request)
    lineas = carrito.lineas()
    if not lineas:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("catalogo")

    form = ConfirmarPedidoForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            try:
                pedido = crear_pedido(
                    request.user,
                    carrito,
                    form.cleaned_data["hora_retiro"],
                    form.cleaned_data["observacion"],
                )
            except StockInsuficiente as error:
                messages.error(request, str(error))
                return redirect("carrito")
            carrito.vaciar()
            messages.success(
                request,
                f"Pedido #{pedido.pk} confirmado. Retíralo a las {pedido.hora_retiro:%H:%M}.",
            )
            return redirect("catalogo")
        messages.error(request, "No se pudo confirmar el pedido. Revisa los errores.")

    return render(request, "cafes/confirmar_pedido.html", {
        "form": form,
        "lineas": lineas,
        "total": sum(l["subtotal"] for l in lineas),
    })