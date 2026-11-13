from .carrito import Carrito


def carrito(request):
    """Unidades del carrito para mostrarlas en el menú del cliente."""
    if request.user.is_authenticated and not request.user.is_staff:
        return {"carrito_unidades": Carrito(request).unidades()}
    return {}
