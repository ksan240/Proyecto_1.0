from django.shortcuts import render

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