from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'), 

    path('carrito/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('error/', views.error_view, name='error'),

    # la pongo al final para q por ejemplo si accedo a /login no piense que login es una marca de coche
    path('add_to_cart/<int:coche_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:coche_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('<str:marca>/', views.coches_por_marca, name='coches_por_marca'),
    path('<str:marca>/<int:coche_id>/', views.detalles_coche, name='detalles_coche'),


]