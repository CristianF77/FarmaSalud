from django.forms import ModelForm
from django import forms

from .models import Item, Producto, Venta, Personal, Cliente


class ItemForm(forms.Form):
    # venta = forms.ModelChoiceField(queryset=Venta.objects.all().values_list('num_vta', flat=True))
    producto = forms.ModelChoiceField(queryset=Producto.objects.all())
    cantidad = forms.IntegerField(label='Ingrese cantidad')
    
class VentaForm(forms.Form):
    METODO_PAGO = (('Efectivo', 'Contado'),('Débito', 'Tarjeta de débito'),('Crédito', 'Tarjeta de crédito'))

    vendedor = forms.ModelChoiceField(required=True, queryset=Personal.objects.filter(cargo='DT'))
    cliente = forms.ModelChoiceField(required=True, queryset=Cliente.objects.all())
    metodo = forms.ChoiceField(choices=METODO_PAGO, label='Método de pago')
   
    
class AñadirStock(ModelForm):
    class Meta:
        model = Producto
        fields = ['cantidad']
    
