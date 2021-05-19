from django.forms import ModelForm
from django import forms

from .models import Item, Producto, Venta, PersonalSucursal, Cliente


# class ItemForm(forms.Form, farmacia):
#     producto = forms.ModelChoiceField(queryset=Producto.objects.all())
#     cantidad = forms.IntegerField(label='Ingrese cantidad')

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ('producto', 'cantidad')


class VentaForm(forms.Form):
    METODO_PAGO = (('Efectivo', 'Contado'), ('Débito',
                   'Tarjeta de débito'), ('Crédito', 'Tarjeta de crédito'))

    vendedor = forms.ModelChoiceField(
        required=True, queryset=PersonalSucursal.objects.filter(cargo='DT'))
    cliente = forms.ModelChoiceField(
        required=True, queryset=Cliente.objects.all())
    metodo = forms.ChoiceField(choices=METODO_PAGO, label='Método de pago')


class AñadirStock(ModelForm):
    class Meta:
        model = Producto
        fields = ['cantidad']


class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'


class BuscarClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['documento']
