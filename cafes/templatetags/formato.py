from django import template

register = template.Library()


@register.filter
def clp(valor):
    """Formatea un entero como pesos chilenos: 1500 -> $1.500"""
    try:
        return "$" + f"{int(valor):,}".replace(",", ".")
    except (TypeError, ValueError):
        return valor
