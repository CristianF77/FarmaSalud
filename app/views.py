from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Producto, PersonalSucursal, Venta, Item, Cliente, Farmacia, User
from .forms import ItemForm, VentaForm, AñadirStock, ClienteForm, BuscarClienteForm, SalesSearchForm, ReportForm
from .utils import calcularImporte, controlarStock, get_cliente_por_id, get_farmacia_por_id, get_vendedor_por_id, get_chart, render_to_pdf, controlar_dt
from django import forms
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.views.generic import View
import datetime
import time
from django.contrib import messages


@login_required
def home(request):
    permiso = None
    username = None
    if request.user.is_authenticated:
        username = request.user
        if controlar_dt(username):
            venta = Venta.objects.all()
            for v in venta:
                v.fecha = v.fecha.strftime('%d-%m-%Y')
            permiso = True
        else:
            venta = None
            permiso = False

    context = {
        'venta': venta,
        'permiso': permiso,
    }
    return render(request, 'app/home.html', context)


@login_required
def productos_stock(request):
    permiso = None
    username = None

    productos = Producto.objects.all()

    if request.user.is_authenticated:
        username = request.user
        if controlar_dt(username):
            permiso = True
            if request.method == 'POST':
                print(request.POST['id'])
                redirect('/stock/add/' + request.POST['id'])

        else:
            permiso = False

    context = {
        'productos': productos,
        'permiso': permiso,
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
    permiso = None
    username = None
    if request.user.is_authenticated:
        username = request.user
        if controlar_dt(username):
            permiso = True
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
                        messages.success(request, "Items creados con éxito")
                        return redirect('/home/')

            else:
                form = ItemForm()
                if 'stock' in request.GET:
                    stock = False
        else:
            form = ItemForm()
            stock = None
            permiso = False

    context = {
        'form': form,
        'stock': False,
        'permiso': permiso,
    }

    return render(request, 'app/item_create.html', context)


@login_required
def venta_create(request):
    submitted = False
    clte_id = request.session.get('clte')
    permiso = None
    username = None

    if request.user.is_authenticated:
        username = request.user
        if controlar_dt(username):
            permiso = True
            if request.method == 'POST':
                form = VentaForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    metodo = cd['metodo']
                    cliente = cd['cliente']
                    vendedor = cd['vendedor']
                    vta = Venta(metodo_pago=metodo,
                                cliente=cliente, vendedor=vendedor)
                    vta.save()
                    messages.success(request, "Venta creado con éxito")
                    return redirect('/venta/' + str(vta.id) + '/item/')
            else:
                form = VentaForm()
                if 'submitted' in request.GET:
                    submitted = True
        else:
            form = VentaForm()
            permiso = False

    context = {
        'form': form,
        'submitted': submitted,
        'permiso': permiso,
    }

    return render(request, 'app/venta_create.html', context)


@login_required
def add_stock(request, pk):
    permiso = None
    username = None
    if request.user.is_authenticated:
        username = request.user
        if controlar_dt(username):
            permiso = True
            producto = Producto.objects.get(pk=pk)
            form = AñadirStock(request.POST)

            if request.method == 'POST':
                if form.is_valid():
                    cant = int(request.POST['cantidad'])
                    producto.cantidad += cant
                    producto.save()
                    messages.success(request, "Producto añadido con éxito")

                    return redirect('/stock/')
        else:
            permiso = False

    context = {
        'form': form,
        'nombre': producto.nombre,
        'permiso': permiso,
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
                request.session['clte'] = cliente.id
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
    form = ClienteForm()
    permiso = None
    username = None

    if request.user.is_authenticated:
        username = request.user
        if controlar_dt(username):
            permiso = True
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
                    messages.success(request, "Cliente creado con éxito")
                    return redirect('/venta/')
            else:
                form = ClienteForm()
                if 'submitted' in request.GET:
                    submitted = True
        else:
            permiso = False

    context = {
        'form': form,
        'submitted': submitted,
        'permiso': permiso,
    }

    return render(request, 'app/add_cliente.html', context)


@login_required
def reportes(request):
    venta_df = None
    df = None
    chart = None
    no_data = None

    search_form = SalesSearchForm(request.POST or None)
    report_form = ReportForm()

    if request.method == 'POST':
        desde = request.POST.get('desde')
        hasta = request.POST.get('hasta')
        chart_type = request.POST.get('chart_type')
        results_by = request.POST.get('results_by')

        vta_qs = Venta.objects.filter(
            fecha__date__lte=hasta, fecha__date__gte=desde)
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
            venta_df.rename({'fecha': 'Fecha', 'importe': 'Importe', 'cliente_id': 'Cliente', 'vendedor_id': 'Vendedor',
                            'farmacia_id': 'Farmacia', 'metodo_pago': 'Método'}, axis=1, inplace=True)

            # venta_df.style.set_properties(**{'text-align': 'center'})

            if results_by == '#1':
                resultado = 'Farmacia'
            elif results_by == '#2':
                resultado = 'Fecha'

            df = venta_df.groupby(resultado, as_index=False)[
                'Importe'].agg('sum')

            # print(df)

            chart = get_chart(chart_type, venta_df, results_by)

            venta_df = venta_df.to_html()

            df = df.to_html(justify='left')

            # time.sleep(2)
            # request.session['desde'] = desde
            # request.session['hasta'] = hasta

            # if results_by == '#1':
            #     resultado = 'Farmacia'
            # elif results_by == '#2':
            #     resultado = 'Fecha'

            # request.session['resultado'] = resultado
            # request.session['venta_df'] = venta_df
            # request.session['chart'] = chart
            # return redirect('/pdf/')

        else:
            no_data = 'No hay datos en el rango indicado'

        if 'exportar' in request.POST:
            # request.session['venta_df'] = venta_df
            # request.session['chart'] = chart

            return redirect('/pdf/')

    context = {
        'search_form': search_form,
        'report_form': report_form,
        'venta_df': venta_df,
        'df': df,
        'chart': chart,
        'no_data': no_data,
    }

    return render(request, 'app/reportes.html', context)

@login_required
def generate_view(request, *args, **kwargs):

    venta_df = request.session.get('venta_df')
    chart = request.session.get('chart')
    desde = request.session.get('desde')
    hasta = request.session.get('hasta')
    resultado = request.session.get('resultado')
    data = {
        'venta_df': venta_df,
        'chart': chart,
        'desde': desde,
        'hasta': hasta,
        'resultado': resultado,
    }
    pdf = render_to_pdf('app/invoice.html', data)
    return HttpResponse(pdf, content_type='application/pdf')
