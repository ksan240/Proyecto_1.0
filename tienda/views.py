from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import Coche, Carrito, Comentario, Venta
import stripe, random, csv
from django.conf import settings
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from collections import Counter
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required

import random

def index(request):
    query = request.GET.get('q', '')
    coches = []
    if query:
        coches = Coche.objects.filter(
            Q(marca__icontains=query) |
            Q(modelo__icontains=query) |
            Q(pais__icontains=query) |
            Q(descripcion__icontains=query)
        )
    return render(request, 'index.html', {'coches': coches, 'query': query})

def ferrari(request):
    return render(request, 'ferrari.html')

def pagani(request):
    return render(request, 'pagani.html')

def lamborghini(request):
    return render(request, 'lamborghini.html')

def mclaren(request):
    return render(request, 'mclaren.html')

def bmw(request):
    return render(request, 'bmw.html')

# Vista del login:

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Redirige al inicio si el login es exitoso
        else:
            # Pasa un mensaje de error al contexto
            return render(request, 'index.html', {'login_error': 'Usuario o contraseña incorrectos'})
    return redirect('index')

# Vista del registro:

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        if username and password1 and password2 and email:
            if password1 != password2:
                error = "Las contraseñas no coinciden."
                return render(request, 'index.html', {'register_error': error})
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password=password1, email=email)
                return redirect('index')
            else:
                error = "El usuario ya existe."
                return render(request, 'index.html', {'register_error': error})
        else:
            error = "Rellena todos los campos."
            return render(request, 'index.html', {'register_error': error})
    return render(request, 'index.html')

# Vista del logout:

def logout_view(request):
    logout(request)
    return redirect('index')

# PARA LA GESTION DE LOS COCHES:

def coches_por_marca(request, marca):

    # Filtrar coches por la marca proporcionada en la URL
    coches = Coche.objects.filter(marca=marca)

    # Obtener modelos únicos de los coches filtrados
    modelos = Coche.objects.filter(marca=marca).values_list('modelo', flat=True).distinct()

    # Obtener países únicos de los coches filtrados
    paises = Coche.objects.filter(marca=marca).values_list('pais', flat=True).distinct()

    # Filtrar por modelo
    modelo = request.GET.get('modelo')
    if modelo:
        coches = coches.filter(modelo__icontains=modelo)

    # Filtrar por año
    año_min = request.GET.get('año_min')
    año_max = request.GET.get('año_max')
    if año_min:
        coches = coches.filter(año__gte=año_min)
    if año_max:
        coches = coches.filter(año__lte=año_max)

    # Filtrar por precio
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    if precio_min:
        coches = coches.filter(precio__gte=precio_min)
    if precio_max:
        coches = coches.filter(precio__lte=precio_max)

    # Filtrar por país
    pais = request.GET.get('pais')
    if pais:
        coches = coches.filter(pais__icontains=pais)

    # Renderizar la plantilla genérica
    return render(request, 'base2.html', {'coches': coches, 'marca': marca, 'paises': paises, 'modelos': modelos})


# PARA LA GESTION DEL CARRITO:


stripe.api_key = settings.STRIPE_SECRET_KEY

# Añadir un coche al carrito
@login_required
def add_to_cart(request, coche_id):
    coche = get_object_or_404(Coche, id=coche_id)

    # Verificar si hay suficiente stock
    if coche.cantidad_disponible < 1:
        return render(request, 'error.html', {'error_message': f"No hay suficiente stock para {coche.marca} {coche.modelo}."})

    # Añadir al carrito o incrementar la cantidad
    carrito_item, created = Carrito.objects.get_or_create(user=request.user, coche=coche)
    if not created:
        carrito_item.cantidad += 1
    else:
        carrito_item.cantidad = 1

    carrito_item.save()
    return redirect('view_cart')

# Ver el carrito

def view_cart(request):
    if not request.user.is_authenticated:
        # Redirigir al inicio y mostrar el popup de login
        return redirect(f"{request.build_absolute_uri('/')}?show_login=true")

    carrito_items = Carrito.objects.filter(user=request.user)
    total = sum(item.coche.precio * item.cantidad for item in carrito_items)
    return render(request, 'carrito.html', {'carrito_items': carrito_items, 'total': total})

# Finalizar la compra

def checkout(request):
    carrito_items = Carrito.objects.filter(user=request.user)
    total = sum(item.coche.precio * item.cantidad for item in carrito_items)

    if request.method == 'POST':
        # Crear una sesión de pago de Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.coche.marca + " " + item.coche.modelo,
                        },
                        'unit_amount': int(item.coche.precio * 100),  # Stripe usa centavos
                    },
                    'quantity': item.cantidad,
                } for item in carrito_items
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cancel/'),
        )
        return redirect(session.url, code=303)

    return render(request, 'checkout.html', {'carrito_items': carrito_items, 'total': total})

# Success y Cancel URL

def success(request):
    # Reducir el stock de los coches comprados
    carrito_items = Carrito.objects.filter(user=request.user)
    for item in carrito_items:
        coche = item.coche
        if item.cantidad > coche.cantidad_disponible:
            return render(request, 'error.html', {'error_message': f"No hay suficiente stock para {coche.marca} {coche.modelo}."})
        coche.cantidad_disponible -= item.cantidad
        coche.save()

    # Limpiar el carrito después de la compra
    carrito_items.delete()
    if request.user.is_authenticated and request.user.email:
        send_mail(
            '¡Gracias por tu compra!',
            'Tu pedido ha sido recibido y está en proceso.',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=True,
        )
    return render(request, 'success.html')

def cancel(request):
    if not request.user.is_authenticated:
        return redirect(f"{request.build_absolute_uri('/')}?show_login=true")

    # Elimina todos los coches del carrito del usuario
    Carrito.objects.filter(user=request.user).delete()
    return render(request, 'cancel.html')

# Eliminar un coche del carrito

def remove_from_cart(request, coche_id):
    if not request.user.is_authenticated:
        return redirect(f"{request.build_absolute_uri('/')}?show_login=true")

    Carrito.objects.filter(user=request.user, coche_id=coche_id).delete()
    return redirect('view_cart')  # Redirigir al carrito después de eliminar

def error_view(request):
    return render(request, 'error.html', {'error_message': 'Ha ocurrido un error.'})

# Views de las paginas con detalles de los coches y comentarios:

def detalles_coche(request, marca, coche_id):
    coche = get_object_or_404(Coche, id=coche_id, marca=marca)
    comentarios = coche.comentarios.all().order_by('-fecha')
    puede_comentar = False
    if request.user.is_authenticated:
        num_comentarios = comentarios.filter(usuario=request.user).count()
        puede_comentar = num_comentarios < 2 # es true sí num_comentarios < 2

    if request.method == 'POST' and puede_comentar:
        texto = request.POST.get('texto')
        valoracion = request.POST.get('valoracion')
        if texto and valoracion:
            Comentario.objects.create(
                coche=coche,
                usuario=request.user,
                texto=texto,
                valoracion=valoracion
            )
            return redirect('detalles_coche', marca=marca, coche_id=coche_id)

    return render(request, 'detalles_coche.html', {
        'coche': coche,
        'comentarios': comentarios,
        'puede_comentar': puede_comentar
    })

def eliminar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    if request.user == comentario.usuario:
        coche = comentario.coche
        marca = coche.marca
        coche_id = coche.id
        comentario.delete()
        return redirect('detalles_coche', marca=marca, coche_id=coche_id)
    return redirect('index')

# Para simular ventas y llevarlas a la tabla venta de la base de datos:

@staff_member_required
def simular_ventas(request):
    usuarios = list(User.objects.all())
    coches = list(Coche.objects.all())
    for _ in range(100):
        user = random.choice(usuarios)
        coche = random.choice(coches)
        cantidad = random.randint(1, 3)
        # Fecha aleatoria entre año de fabricación y 2025
        start = datetime(coche.año, 1, 1)
        end = datetime(2025, 12, 31)
        if start > end:
            # Si el año de fabricación es después de 2025, pon la fecha en 2025
            fecha_random = end
        else:
            delta = end - start
            fecha_random = start + timedelta(days=random.randint(0, delta.days))
        Venta.objects.create(usuario=user, coche=coche, cantidad=cantidad, fecha=fecha_random)
    return redirect('estadisticas')  # Redirige a la página de estadísticas

# Para coger los datos de las ventas y mostrarlos en una página de estadísticas:

@staff_member_required
def estadisticas_ventas(request):
    ventas = Venta.objects.all()
    total_ventas = ventas.count()

    # Porcentaje de ventas por marca
    marcas = Coche.OPCIONES_MARCA
    ventas_por_marca = {marca[0]: 0 for marca in marcas}
    for venta in ventas:
        ventas_por_marca[venta.coche.marca] += venta.cantidad
    total_coches_vendidos = sum(ventas_por_marca.values())
    porcentaje_por_marca = {marca: (cantidad / total_coches_vendidos * 100) if total_coches_vendidos else 0 for marca, cantidad in ventas_por_marca.items()}

    # Porcentaje de ventas por rango de año de compra (fecha de la venta)
    rangos = [
        (1990, 2000),
        (2000, 2010),
        (2010, 2020),
        (2020, 2026),
    ]
    ventas_por_rango = {}
    for inicio, fin in rangos:
        ventas_en_rango = ventas.filter(fecha__year__gte=inicio, fecha__year__lt=fin).count()
        porcentaje = (ventas_en_rango / total_ventas * 100) if total_ventas else 0
        ventas_por_rango[f"{inicio}-{fin-1}"] = porcentaje

    # Ventas por país de origen
    ventas_por_pais = {}
    for venta in ventas:
        pais = venta.coche.pais
        ventas_por_pais[pais] = ventas_por_pais.get(pais, 0) + venta.cantidad

    # Ventas por año de fabricación
    ventas_por_año = {}
    for venta in ventas:
        año = venta.coche.año
        ventas_por_año[año] = ventas_por_año.get(año, 0) + venta.cantidad

    # Top 3 meses con más ventas (solo mes, todos los años)
    ventas_por_mes = {}
    for venta in ventas:
        mes = venta.fecha.month
        ventas_por_mes[mes] = ventas_por_mes.get(mes, 0) + venta.cantidad
    top_3_meses = sorted(ventas_por_mes.items(), key=lambda x: x[1], reverse=True)[:3]
    meses_es = [
        "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    top_3_meses_nombre = [(meses_es[mes], cantidad) for mes, cantidad in top_3_meses]

    # Top 5 modelos más vendidos
    contador_modelos = Counter()
    for venta in ventas:
        modelo = f"{venta.coche.marca} {venta.coche.modelo}"
        contador_modelos[modelo] += venta.cantidad
    top_5_modelos = contador_modelos.most_common(5)

    return render(request, 'estadisticas.html', {
        'marcas_labels': list(porcentaje_por_marca.keys()),
        'marcas_data': list(porcentaje_por_marca.values()),
        'rangos_labels': list(ventas_por_rango.keys()),
        'rangos_data': list(ventas_por_rango.values()),
        'pais_labels': list(ventas_por_pais.keys()),
        'pais_data': list(ventas_por_pais.values()),
        'año_labels': list(ventas_por_año.keys()),
        'año_data': list(ventas_por_año.values()),
        'modelos_labels': [m[0] for m in top_5_modelos],
        'modelos_data': [m[1] for m in top_5_modelos],
        'meses_labels': [m[0] for m in top_3_meses_nombre],
        'meses_data': [m[1] for m in top_3_meses_nombre],
    })

# Para descargar las ventas en un archivo CSV:

@staff_member_required
def descargar_ventas(request):
    ventas = Venta.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ventas.csv"'
    writer = csv.writer(response)
    writer.writerow(['Usuario', 'Marca', 'Modelo', 'Cantidad', 'Año', 'Precio', 'Fecha'])
    for venta in ventas:
        writer.writerow([
            venta.usuario.username,
            venta.coche.marca,
            venta.coche.modelo,
            venta.cantidad,
            venta.coche.año,
            venta.coche.precio,
            venta.fecha.strftime('%Y-%m-%d %H:%M')
        ])
    return response

# Para descargar las estadisticas en un archivo CSV:

@staff_member_required
def descargar_estadisticas(request):
    ventas = Venta.objects.all()
    total_ventas = ventas.count()
    marcas = Coche.OPCIONES_MARCA
    ventas_por_marca = {marca[0]: 0 for marca in marcas}
    for venta in ventas:
        ventas_por_marca[venta.coche.marca] += venta.cantidad
    total_coches_vendidos = sum(ventas_por_marca.values())
    porcentaje_por_marca = {marca: (cantidad / total_coches_vendidos * 100) if total_coches_vendidos else 0 for marca, cantidad in ventas_por_marca.items()}

    # Porcentaje de ventas por rango de año de compra (fecha de la venta)
    rangos = [
        (1990, 2000),
        (2000, 2010),
        (2010, 2020),
        (2020, 2030),
    ]
    ventas_por_rango = {}
    for inicio, fin in rangos:
        ventas_en_rango = ventas.filter(fecha__year__gte=inicio, fecha__year__lt=fin).count()
        porcentaje = (ventas_en_rango / total_ventas * 100) if total_ventas else 0
        ventas_por_rango[f"{inicio}-{fin-1}"] = porcentaje

    # Ventas por país de origen
    ventas_por_pais = {}
    for venta in ventas:
        pais = venta.coche.pais
        ventas_por_pais[pais] = ventas_por_pais.get(pais, 0) + venta.cantidad

    # Ventas por año de fabricación
    ventas_por_año = {}
    for venta in ventas:
        año = venta.coche.año
        ventas_por_año[año] = ventas_por_año.get(año, 0) + venta.cantidad

    # Top 5 modelos más vendidos
    contador_modelos = Counter()
    for venta in ventas:
        modelo = f"{venta.coche.marca} {venta.coche.modelo}"
        contador_modelos[modelo] += venta.cantidad
    top_5_modelos = contador_modelos.most_common(5)

    # Top 3 meses con más ventas (solo mes, todos los años)
    ventas_por_mes = {}
    for venta in ventas:
        mes = venta.fecha.month
        ventas_por_mes[mes] = ventas_por_mes.get(mes, 0) + venta.cantidad
    top_3_meses = sorted(ventas_por_mes.items(), key=lambda x: x[1], reverse=True)[:3]
    meses_es = [
        "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    top_3_meses_nombre = [(meses_es[mes], cantidad) for mes, cantidad in top_3_meses]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="estadisticas_ventas.csv"'
    writer = csv.writer(response)
    writer.writerow(['Estadística', 'Valor'])
    writer.writerow(['Total ventas', total_ventas])
    for marca, porcentaje in porcentaje_por_marca.items():
        writer.writerow([f'Porcentaje ventas {marca}', f'{porcentaje:.2f}%'])

    writer.writerow([])
    writer.writerow(['Porcentaje de ventas por rango de año de compra'])
    for rango, porcentaje in ventas_por_rango.items():
        writer.writerow([f'Ventas {rango}', f'{porcentaje:.2f}%'])

    writer.writerow([])
    writer.writerow(['Ventas por país de origen'])
    for pais, cantidad in ventas_por_pais.items():
        writer.writerow([pais, cantidad])

    writer.writerow([])
    writer.writerow(['Ventas por año de fabricación'])
    for año, cantidad in ventas_por_año.items():
        writer.writerow([año, cantidad])

    writer.writerow([])
    writer.writerow(['Top 5 modelos más vendidos'])
    for modelo, cantidad in top_5_modelos:
        writer.writerow([modelo, cantidad])

    writer.writerow([])
    writer.writerow(['Top 3 meses con más ventas (todos los años)'])
    for mes, cantidad in top_3_meses_nombre:
        writer.writerow([mes, cantidad])

    return response