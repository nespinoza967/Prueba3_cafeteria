import re
from django import forms
from .models import Categoria, Producto

CODIGO_RE = re.compile(r"^CAF-\d{3}$")

class BootstrapMixin:
    """Agrega las clases de Bootstrap a los widgets y marca los campos con error."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = "form-select"
            else:
                widget.attrs["class"] = "form-control"

    def is_valid(self):
        valido = super().is_valid()
        for nombre in self.errors:
            if nombre in self.fields:
                self.fields[nombre].widget.attrs["class"] += " is-invalid"
        return valido


class CategoriaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "activa"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}


class ProductoForm(BootstrapMixin, forms.ModelForm):
    precio = forms.IntegerField(label="Precio")
    stock = forms.IntegerField(label="Stock", initial=0)

    class Meta:
        model = Producto
        fields = ["categoria", "codigo", "nombre", "precio", "stock", "disponible"]
        widgets = {"codigo": forms.TextInput(attrs={"placeholder": "CAF-000"})}

    def clean_codigo(self):
        codigo = self.cleaned_data["codigo"].strip().upper()
        if not CODIGO_RE.match(codigo):
            raise forms.ValidationError("El código debe tener el formato CAF-000 (tres dígitos).")
        return codigo

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio < 100 or precio > 20000:
            raise forms.ValidationError("El precio debe estar entre $100 y $20.000.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock