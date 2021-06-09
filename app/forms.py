from django.forms import ModelForm
from django import forms

from .models import Item, Producto, Venta, PersonalSucursal, Cliente, Reportes, Farmacia


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ('producto', 'cantidad')


class VentaForm(ModelForm):
    class Meta:
        model = Venta
        fields = ('metodo_pago', 'cliente')

# class VentaForm(forms.Form):
#     METODO_PAGO = (('Efectivo', 'Contado'), ('Débito',
#                    'Tarjeta de débito'), ('Crédito', 'Tarjeta de crédito'))

#     vendedor = forms.ModelChoiceField(
#         required=True, queryset=PersonalSucursal.objects.filter(cargo='DT'))
#     cliente = forms.ModelChoiceField(
#         required=True, queryset=Cliente.objects.all())
#     metodo = forms.ChoiceField(choices=METODO_PAGO, label='Método de pago')


class FarmaciaForm(forms.Form):
    farmacia = forms.ModelChoiceField(
        required=True, queryset=Farmacia.objects.all())


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


class ReportForm(forms.ModelForm):
    class Meta:
        model = Reportes
        fields = ('name', 'remarks')


CHART_CHOICES = (
    ('#1', 'Bar chart'),
    ('#2', 'Pie chart'),
    ('#3', 'Line chart'),
)

RESULT_CHOICES = (
    ('#1', 'farmacia'),
    ('#2', 'fecha'),
)


class SalesSearchForm(forms.Form):
    desde = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hasta = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    chart_type = forms.ChoiceField(choices=CHART_CHOICES)
    results_by = forms.ChoiceField(choices=RESULT_CHOICES)


class BuscarProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre']
