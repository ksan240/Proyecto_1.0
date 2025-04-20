from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from .models import Coche

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

    # Renderizar la plantilla genérica
    return render(request, 'base2.html', {'coches': coches, 'marca': marca})