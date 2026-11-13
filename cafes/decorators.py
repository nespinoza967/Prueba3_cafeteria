from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def encargado_required(view):
    """Solo usuarios con is_staff. Un cliente recibe 403."""
    @login_required
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return _wrapped


def cliente_required(view):
    """Solo clientes (no is_staff). Un encargado recibe 403."""
    @login_required
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return _wrapped
