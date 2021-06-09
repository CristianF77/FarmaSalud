from django.urls import path
from . import views
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('pdf/', views.generate_view, name='pdf'),

    path('reportes/', views.reportes, name='reportes'),

    path('venta/item/<int:pk>/', views.item_create, name='item-create'),
    path('venta/<int:pk>', views.venta_create, name='venta-create'),
    path('venta/list/', VentaList.as_view(), name='venta-list'),
    path('venta/<int:pk>/', VentaDetail.as_view(), name='venta-detail'),
    path('venta/edit/<int:pk>/', VentaUpdate.as_view(), name='venta-update'),
    path('venta/delete/<int:pk>/', VentaDelete.as_view(), name='venta-delete'),
    path('venta/final/<int:pk>/', views.venta_final, name='venta-final'),


    path('cliente/list/', ClienteList.as_view(), name='cliente-list'),
    path('cliente/<int:pk>/', ClienteDetail.as_view(), name='cliente-detail'),
    path('cliente/create/', ClienteCreate.as_view(), name='cliente-create'),
    path('cliente/edit/<int:pk>/', ClienteUpdate.as_view(), name='cliente-update'),
    path('cliente/delete/<int:pk>/',
         ClienteDelete.as_view(), name='cliente-delete'),

    path('producto/list/', ProductoList.as_view(), name='producto-list'),
    path('producto/<int:pk>/', ProductoDetail.as_view(), name='producto-detail'),
    path('producto/create/', ProductoCreate.as_view(), name='producto-create'),
    path('producto/edit/<int:pk>/',
         ProductoUpdate.as_view(), name='producto-update'),
    path('producto/delete/<int:pk>/',
         ProductoDelete.as_view(), name='producto-delete'),

    path('', auth_views.LoginView.as_view(
        template_name='app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='app/logout.html'), name='logout'),

]
