# Respuestas de la IA

Respuestas breves a cada prompt usado durante el desarrollo de Cafetería Fiores.

---

## 1. Análisis de la evaluación y plan

**Prompt:** "Esta es la evaluacion, necesito que me vayas guiando sobre el tema, analiza el pdf y dame un plan, OJO no cambies nada del codigo sin mi permiso"

**Respuesta:**
Revisé la evaluación. Propongo avanzar por fases, sin tocar código sin tu permiso:

- **Fase 0:** configurar `settings.py` (app `cafes`, idioma `es-cl`, zona horaria, base de datos).
- **Fase 1:** modelos `Categoria`, `Producto`, `Pedido` y `DetallePedido`, migraciones y admin.
- **Fase 2 (RF-01/02):** login/logout, roles (cliente/encargado), protección y sesión.
- **Fase 3 (RF-03):** catálogo para clientes.
- **Fase 4 (RF-04):** CRUD de categorías y productos para el encargado.
- **Fase 5 (RF-05):** carrito y confirmación de pedido con descuento de stock.
- **Fase 6 (RF-06):** historial y cancelación (cliente) y avance de estados (encargado).
- **Cierre:** pruebas, bitácora y README.

---

## 2. Fase 0 lista, comenzar con `models.py`

**Prompt:** "Realizamos los cambios de la fase 0: donde desarrollamos los cambios necesarios de settings.py y ahora que ya tenemos la BD, empecemos con el models.py"

**Respuesta:**
Con la BD lista, `models.py` queda con 4 modelos:

- **Categoria:** `nombre` único, `descripcion`, `activa`.
- **Producto:** FK a `Categoria` con `PROTECT`, `codigo` único, `nombre`, `precio`, `stock`, `disponible`, `creado`.
- **Pedido:** FK al usuario (`cliente`), `fecha`, `hora_retiro`, `estado` con choices (Pendiente, En preparación, Listo, Entregado, Cancelado), `total`, `observacion`.
- **DetallePedido:** FK a `Pedido` (`CASCADE`) y a `Producto` (`PROTECT`), `cantidad`, `precio_unitario`, `subtotal`, con restricción de producto único por pedido.

Después: `makemigrations`, `migrate`, registrar los modelos en `admin.py` y crear los usuarios de prueba (un cliente y un encargado con `is_staff`).

---

## 3. Fase 2: login, roles, seguridad y sesión

**Prompt:** "vamos con la Fase, que vendria siendo el login y logout, vistas por rol, proteccion antes sql injectos, sesion de 30 minutos y el menú con el usuario y su rol"

**Respuesta:**

- **Login/Logout:** `LoginView` y `LogoutView` de Django; el logout se hace por POST.
- **Vistas por rol:** decoradores `cliente_required` y `encargado_required` (`decorators.py`) basados en `is_staff`; si el rol no corresponde, responde 403.
- **SQL injection:** se usa solo el ORM de Django (consultas parametrizadas), nunca SQL armado con texto. Además, CSRF en todos los formularios.
- **Sesión de 30 minutos:** `SESSION_COOKIE_AGE = 1800` y `SESSION_SAVE_EVERY_REQUEST = True` (expira tras 30 min sin actividad).
- **Menú:** en `base.html` se muestra `request.user.username` y su rol (Encargado/Cliente), con enlaces según el rol.

---

## 4. Fase 3: catálogo para clientes (RF-03)

**Prompt:** "Iniciamos la Fase 4: Rf-03 entrando como cliente1 y como encargado. La siguiente es la Fase 3: catálogo para clientes (RF-03)"

**Respuesta:**
El catálogo (`views.catalogo`) muestra solo productos **disponibles y de categorías activas**, con búsqueda por nombre (`?q=`) y filtro por categoría (`?categoria=`). Lo ve el cliente (`cliente1`); el encargado va a su panel. Para probar: entrar con cada usuario y verificar que cada uno ve solo lo que le corresponde.

---

## 5. Mejorar el diseño de los HTML de RF-04 y RF-05

**Prompt:** "Ya termine la parte de RF-04 y RF-05, en temas de backend no utilice IA, pero en la parte de HTML mejora y deja mas bonito los archivos, _campo.html, carrito_html, categoria_detalle.html, categoria_lista.html, confirmar_eliminar.html, confirmar_pedido y form.html"

**Respuesta:**
Solo se mejora la parte visual, sin tocar el backend:

- Tarjetas (cards) con encabezado y sombras suaves.
- Tablas con estilo, filas alternadas y botones de acción agrupados.
- `_campo.html` con etiqueta, ayuda y errores de validación destacados.
- `carrito.html` y `confirmar_pedido.html` con resumen claro del total.
- `confirmar_eliminar.html` con alerta de advertencia y botón rojo.
- Íconos y badges para estados (activa/inactiva, stock).

---

## 6. RF-06: seguimiento de pedidos

**Prompt:** "Vamos con la parte del RF-06 donde el cliente ve su historial de pedidos con el detalle y el total, puede cancelar un pedido Pendiente (repone stock); un cliente no puede ver ni modificar pedidos ajenos; el encargado ve los pedidos del día filtrados por estado y los avanza en orden sin retroceder ni saltarse estados"

**Respuesta:**
Se implementa en `views_pedidos.py`:

- **Historial (`mis_pedidos`):** filtra `Pedido.objects.filter(cliente=request.user)` y muestra detalle y total.
- **Detalle (`pedido_detalle`):** `get_object_or_404(..., pk=pk, cliente=request.user)`; si el cliente cambia el id en la URL por uno ajeno, recibe **404**.
- **Cancelar (`pedido_cancelar`):** solo por POST y solo si está `PENDIENTE`; dentro de una transacción repone el stock con `F("stock") + cantidad` y cambia el estado a `CANCELADO`.
- **Pedidos del día (`pedidos_dia`):** solo encargado; filtra por `fecha__date=hoy` y por el estado elegido en `?estado=`.
- **Avanzar (`pedido_avanzar`):** usa el diccionario `SIGUIENTE_ESTADO` (Pendiente → En preparación → Listo → Entregado), así no se puede retroceder ni saltar estados. También compara el estado enviado con el actual para evitar avances dobles.
