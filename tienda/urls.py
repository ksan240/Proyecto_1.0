from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ferrari/', views.ferrari, name='ferrari'),
    path('pagani/', views.pagani, name='pagani'),
    path('lamborghini/', views.lamborghini, name='lamborghini'),
    path('mclaren/', views.mclaren, name='mclaren'),
    path('bmw/', views.bmw, name='bmw'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'), 
]