from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Producto, PersonalSucursal, Venta, Item, Cliente, Farmacia
from .forms import ItemForm, VentaForm, AñadirStock, ClienteForm, BuscarClienteForm, SalesSearchForm, ReportForm
from .utils import calcularImporte, controlarStock, get_cliente_por_id, get_farmacia_por_id, get_vendedor_por_id, get_chart
from django import forms
from django.contrib.auth.decorators import login_required
import pandas as pd


@login_required
def home(request):
    venta = Venta.objects.all()
    # Calucalar importe
    context = {
        'venta': venta,
    }
    return render(request, 'app/home.html', context)


def productos_stock(request):
    productos = Producto.objects.all()

    if request.method == 'POST':
        print(request.POST['id'])
        redirect('/stock/add/' + request.POST['id'])

    context = {
        'productos': productos,
    }
    return render(request, 'app/stock.html', context)


@login_required
def personal(request):
    personal_suc = PersonalSucursal.objects.filter(cargo='DT')
    context = {
        'personal_suc': personal_suc,
    }
    return render(request, 'app/personal.html', context)


@login_required
def item_create(request, num_vta):
    stock = False
    vta = Venta.objects.get(id=num_vta)
    suc = vta.farmacia

    # Se excluyen los productos sin stock
    ItemForm.base_fields['producto'] = forms.ModelChoiceField(
        queryset=Producto.objects.filter(farmacia=suc).exclude(cantidad=0))

    if request.method == 'POST':

        form = ItemForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            producto = cd['producto']
            cantidad = cd['cantidad']
            i = Item(producto=producto, cantidad=cantidad)
            i.venta = Venta.objects.get(id=num_vta)

            # Se controlar si hay stock suficiente, True -> reduce la cantidad
            if controlarStock(producto, cantidad):
                i.save()
            else:
                # no hay stock
                stock = True
                return redirect('/venta/' + str(num_vta) + '/item/no_stock?stock=True')
                pass

            if 'crear-otro' in request.POST:
                return redirect('/venta/' + str(num_vta) + '/item/')
            if 'submitted' in request.POST:
                calcularImporte(num_vta)
                return redirect('/home/')

    else:
        form = ItemForm()
        if 'stock' in request.GET:
            stock = False

    context = {
        'form': form,
        'stock': False,
    }

    return render(request, 'app/item_create.html', context)


@login_required
def venta_create(request):
    submitted = False
    clte_id = request.session.get('clte')
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            metodo = cd['metodo']
            cliente = cd['cliente']
            vendedor = cd['vendedor']
            vta = Venta(metodo_pago=metodo, cliente=cliente, vendedor=vendedor)
            vta.save()
            return redirect('/venta/' + str(vta.id) + '/item/')
    else:
        form = VentaForm()
        if 'submitted' in request.GET:
            submitted = True

    context = {
        'form': form,
        'submitted': submitted
    }

    return render(request, 'app/venta_create.html', context)


@login_required
def add_stock(request, pk):
    producto = Producto.objects.get(pk=pk)
    form = AñadirStock(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            cant = int(request.POST['cantidad'])
            producto.cantidad += cant
            producto.save()

            return redirect('/home/')

    context = {
        'form': form,
    }
    return render(request, 'app/add_stock.html', context)


@login_required
def buscar_cliente(request):

    form = BuscarClienteForm(request.POST)

    if request.method == 'POST':

        if form.is_valid():
            clean_doc = form.cleaned_data['documento']
            print('Request: ', clean_doc)
            cliente = Cliente.objects.get(documento=clean_doc)

            if cliente.documento == clean_doc:
                print('Query: ', cliente.documento)
                request.session.flush()
                request.session['clte'] = c.id
                return redirect('/venta/')
            else:
                return redirect('/cliente/add/')
    context = {
        'form': form,
    }
    return render(request, 'app/buscar_cliente.html', context)


@login_required
def add_cliente(request):
    submitted = False
    if request.method == 'POST':
        if 'existe_cliente' in request.POST:
            return redirect('/venta/')

        form = ClienteForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            documento = cd['documento']
            nombre = cd['nombre']
            apellido = cd['apellido']
            direccion = cd['direccion']
            telefono = cd['telefono']
            email = cd['email']
            obra_social = cd['obra_social']
            clte = Cliente(documento=documento, nombre=nombre, apellido=apellido,
                           direccion=direccion, telefono=telefono, email=email, obra_social=obra_social)
            clte.save()
            request.session['clte'] = clte.id
            return redirect('/venta/')
    else:
        form = ClienteForm()
        if 'submitted' in request.GET:
            submitted = True

    context = {
        'form': form,
        'submitted': submitted
    }

    return render(request, 'app/add_cliente.html', context)


@login_required
def reportes(request):
    sales_df = None
    positions_df = None
    merged_df = None
    df = None
    chart = None
    no_data = None

    search_form = SalesSearchForm(request.POST or None)
    report_form = ReportForm()

    if request.method == 'POST':
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        chart_type = request.POST.get('chart_type')
        results_by = request.POST.get('results_by')

        vta_qs = Venta.objects.filter(
            fecha__date__lte=date_to, fecha__date__gte=date_from)
        # print(vta_qs)

        if len(vta_qs) > 0:
            venta_df = pd.DataFrame(vta_qs.values())
            # print(venta_df)
            venta_df['cliente_id'] = venta_df['cliente_id'].apply(
                get_cliente_por_id)
            venta_df['vendedor_id'] = venta_df['vendedor_id'].apply(
                get_vendedor_por_id)
            venta_df['farmacia_id'] = venta_df['farmacia_id'].apply(
                get_farmacia_por_id)
            venta_df['fecha'] = venta_df['fecha'].apply(
                lambda x: x.strftime('%d-%m-%Y'))
            venta_df.rename({'cliente_id': 'cliente', 'vendedor_id': 'vendedor',
                            'farmacia_id': 'farmacia', 'metodo_pago': 'método'}, axis=1, inplace=True)
            # print('#################################################')
            # print(venta_df)

            df = venta_df.groupby('fecha', as_index=False)[
                'importe'].agg('sum')
            # print(df)

            chart = get_chart(chart_type, venta_df, results_by)

            venta_df = venta_df.to_html()
            df = df.to_html()

        else:
            no_data = 'No data is available in this date range'

    context = {
        'search_form': search_form,
        'report_form': report_form,
        'venta_df': venta_df,
        'df': df,
        'chart': chart,
        'no_data': no_data,
    }

    return render(request, 'app/reportes.html', context)
