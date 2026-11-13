from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.inicio, name="inicio"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("encargado/", views.panel_encargado, name="panel_encargado"),

    path("encargado/categorias/", views.categoria_lista, name="categoria_lista"),
    path("encargado/categorias/nueva/", views.categoria_crear, name="categoria_crear"),
    path("encargado/categorias/<int:pk>/", views.categoria_detalle, name="categoria_detalle"),
    path("encargado/categorias/<int:pk>/editar/", views.categoria_editar, name="categoria_editar"),
    path("encargado/categorias/<int:pk>/eliminar/", views.categoria_eliminar, name="categoria_eliminar"),

    path("encargado/productos/", views.producto_lista, name="producto_lista"),
    path("encargado/productos/nuevo/", views.producto_crear, name="producto_crear"),
    path("encargado/productos/<int:pk>/", views.producto_detalle, name="producto_detalle"),
    path("encargado/productos/<int:pk>/editar/", views.producto_editar, name="producto_editar"),
    path("encargado/productos/<int:pk>/eliminar/", views.producto_eliminar, name="producto_eliminar"),
]