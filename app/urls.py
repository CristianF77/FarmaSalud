from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('pdf/', views.generate_view, name='pdf'),
    path('stock/add/<int:pk>', views.add_stock, name='add-stock'),
    path('stock/', views.productos_stock, name='stock'),
    path('stock/all/', views.stock_total, name='stock-total'),

    path('personal/', views.personal, name='personal'),
    path('reportes/', views.reportes, name='reportes'),
    path('cliente/', views.buscar_cliente, name='buscar-cliente'),
    path('cliente/add/', views.add_cliente, name='crear-cliente'),

    path('venta/<int:num_vta>/item/', views.item_create, name='item-create'),
    path('venta/', views.venta_create, name='venta-create'),

    path('',auth_views.LoginView.as_view(template_name = 'app/login.html'), name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name = 'app/logout.html'), name='logout'), 

]
