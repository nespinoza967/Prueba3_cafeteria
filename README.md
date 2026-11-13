# ☕ Cafetería Fiores

Aplicación web en Django para que los estudiantes de la cafetería armen su pedido desde el celular, elijan una hora de retiro y lo pasen a buscar listo.

**Asignatura:** Programación Back End (TI3041) · Evaluación N°3

## Requisitos

- Python 3.12 o superior (desarrollado con Python 3.14)
- pip
- Conexión a internet para cargar los estilos de Bootstrap desde CDN

## Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/nespinoza967/Prueba3_cafeteria.git
cd Prueba3_cafeteria

# 2. Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear la base de datos SQLite
python manage.py migrate

# 5. Cargar los datos de prueba
python manage.py loaddata datos_prueba

# 6. Levantar el servidor
python manage.py runserver
```

Abrir **http://127.0.0.1:8000/** e iniciar sesión con alguno de los usuarios de prueba.

## Usuarios de prueba

| Usuario     | Contraseña  | Rol                          |
|-------------|-------------|------------------------------|
| `encargado` | `fiores123` | Encargado (`is_staff`)       |
| `cliente1`  | `fiores123` | Cliente                      |
| `cliente2`  | `fiores123` | Cliente                      |

Para entrar a Django Admin (`/admin/`) se necesita un superusuario, que no viene en los datos de prueba:

```bash
python manage.py createsuperuser
```

## Datos de prueba

El archivo `cafes/fixtures/datos_prueba.json` contiene:

- **4 categorías:** Cafés, Bebidas frías, Sándwiches y Pastelería.
- **20 productos** (códigos `CAF-001` a `CAF-020`), entre ellos:
  - sin stock: Latte vainilla, Té helado y Brownie;
  - no disponibles: Mocaccino y Wrap vegetariano.
- **3 usuarios:** un encargado y dos clientes.

## Funcionalidades

| Requerimiento | Rol | Ruta |
|---|---|---|
| RF-01 · Administración de modelos | Superusuario | `/admin/` |
| RF-02 · Inicio y cierre de sesión | Todos | `/login/` |
| RF-03 · Catálogo con búsqueda y filtro | Cliente | `/catalogo/` |
| RF-04 · Gestión de categorías | Encargado | `/encargado/categorias/` |
| RF-04 · Gestión de productos | Encargado | `/encargado/productos/` |
| RF-05 · Carrito y confirmación del pedido | Cliente | `/carrito/` |
| RF-06 · Historial y cancelación de pedidos | Cliente | `/mis-pedidos/` |
| RF-06 · Pedidos del día y avance de estados | Encargado | `/encargado/pedidos/` |

### Reglas principales

- Todas las páginas exigen iniciar sesión. Un cliente que entra a una dirección del encargado (o al revés) recibe **acceso denegado (403)**.
- La sesión expira tras **30 minutos** sin actividad.
- No se puede eliminar una categoría con productos ni un producto que figure en algún pedido.
- Un cliente solo puede ver y cancelar sus propios pedidos; si cambia el id en la URL recibe un error 404.
- Los estados del pedido avanzan en orden: **Pendiente → En preparación → Listo → Entregado**. Solo un pedido Pendiente se puede cancelar, y al cancelarlo se repone el stock.

## Estructura del proyecto

```
CafeteriaFiores/        Configuración del proyecto (settings, urls)
cafes/
├── models.py           Categoria, Producto, Pedido, DetallePedido
├── admin.py            Configuración de Django Admin
├── decorators.py       Control de acceso por rol (cliente / encargado)
├── views.py            Catálogo, gestión del catálogo, carrito y confirmación
├── views_pedidos.py    Seguimiento de pedidos
├── forms.py            Formularios y validaciones
├── carrito.py          Carrito en sesión
├── templatetags/       Filtro |clp para precios en pesos chilenos
├── fixtures/           Datos de prueba
└── templates/          Plantillas HTML
```

## Documentación adicional

- `BITACORA_IA.md`: registro del uso de IA durante el desarrollo.
