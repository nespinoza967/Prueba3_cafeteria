from django.contrib.auth import views as auth_views
from django.urls import path

from . import views, views_pedidos

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

    path("carrito/", views.carrito_ver, name="carrito"),
    path("carrito/agregar/<int:pk>/", views.carrito_agregar, name="carrito_agregar"),
    path("carrito/actualizar/<int:pk>/", views.carrito_actualizar, name="carrito_actualizar"),
    path("carrito/quitar/<int:pk>/", views.carrito_quitar, name="carrito_quitar"),
    path("carrito/vaciar/", views.carrito_vaciar, name="carrito_vaciar"),
    path("carrito/confirmar/", views.pedido_confirmar, name="pedido_confirmar"),

    path("mis-pedidos/", views_pedidos.mis_pedidos, name="mis_pedidos"),
    path("mis-pedidos/<int:pk>/", views_pedidos.pedido_detalle, name="pedido_detalle"),
    path("mis-pedidos/<int:pk>/cancelar/", views_pedidos.pedido_cancelar, name="pedido_cancelar"),
    path("encargado/pedidos/", views_pedidos.pedidos_dia, name="pedidos_dia"),
    path("encargado/pedidos/<int:pk>/avanzar/", views_pedidos.pedido_avanzar, name="pedido_avanzar"),
]
