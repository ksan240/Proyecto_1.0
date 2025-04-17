from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout


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