from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Coche, Carrito
import stripe
from django.conf import settings

def index(request):
    return render(request, 'index.html')

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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            # Pasa los errores al contexto
            return render(request, 'index.html', {'register_form': form, 'register_error': form.errors})
    else:
        form = UserCreationForm()
    return render(request, 'index.html', {'register_form': form})

# Vista del logout:

def logout_view(request):
    logout(request)
    return redirect('index')

# PARA LA GESTION DE LOS COCHES:


def coches_por_marca(request, marca):
    # Filtrar coches por la marca proporcionada en la URL
    coches = Coche.objects.filter(marca=marca)

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

    paises = ['Italia', 'Alemania', 'Reino Unido']

    # Renderizar la plantilla genérica
    return render(request, 'base2.html', {'coches': coches, 'marca': marca, 'paises': paises})


# PARA LA GESTION DEL CARRITO:


stripe.api_key = settings.STRIPE_SECRET_KEY

# Añadir un coche al carrito

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
    return render(request, 'success.html')

def cancel(request):
    return render(request, 'cancel.html')

def error_view(request):
    return render(request, 'error.html', {'error_message': 'Ha ocurrido un error.'})

# Views de las paginas con detalles de los coches:

def detalles_coche(request, marca, coche_id):
    coche = get_object_or_404(Coche, id=coche_id, marca=marca)
    return render(request, 'detalles_coche.html', {'coche': coche})