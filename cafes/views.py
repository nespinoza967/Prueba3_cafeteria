from django.shortcuts import redirect, render

from .decorators import cliente_required, encargado_required
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
