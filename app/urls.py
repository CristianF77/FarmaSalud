from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    
    path('stock/add/<int:pk>', views.add_stock, name='add-stock'),
    path('stock/', views.productos_stock, name='stock'),

    path('personal/', views.personal, name='personal'),

    path('venta/<int:num_vta>/item/', views.item_create, name='item-create'),
    path('venta/', views.venta_create, name='venta-create'),

    
    

]
