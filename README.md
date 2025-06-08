# CarSan Luxury

CarSan Luxury es una plataforma web desarrollada con Django para la gestión y venta de coches de lujo. Permite a los usuarios registrarse, iniciar sesión, explorar coches por marca, añadirlos al carrito, realizar compras con Stripe y dejar comentarios y valoraciones. Incluye un panel de estadísticas de ventas y una función para simular ventas y probar el sistema.

## Funcionalidades principales

- Registro y login de usuarios
- Catálogo de coches filtrable por marca
- Carrito de compra y gestión de stock
- Pagos integrados con Stripe
- Comentarios y valoraciones en cada coche
- Estadísticas de ventas y simulación de ventas
- Descarga de datos en CSV

## Tecnologías usadas

- Django (backend)
- Bootstrap (frontend)
- PostgreSQL/SQLite (base de datos)
- Stripe (pagos)
- Render (despliegue)
- GitHub (control de versiones)

## Instalación rápida

1. Clona el repositorio.
2. Instala las dependencias:  
   `pip install -r requirements.txt`
3. Realiza las migraciones:  
   `python manage.py migrate`
4. (Opcional) Carga datos de ejemplo:  
   `python manage.py loaddata data.json`
5. Ejecuta el servidor:  
   `python manage.py runserver`

## Licencia

Proyecto realizado como TFG. Uso educativo.
