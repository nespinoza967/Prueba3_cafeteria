from django.shortcuts import redirect, render

from .decorators import cliente_required, encargado_required


def inicio(request):
    """Redirige a la página principal según el rol."""
    if request.user.is_staff:
        return redirect("panel_encargado")
    return redirect("inicio_cliente")


@cliente_required
def inicio_cliente(request):
    return render(request, "cafes/inicio_cliente.html")


@encargado_required
def panel_encargado(request):
    return render(request, "cafes/panel_encargado.html")
