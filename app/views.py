from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Producto, PersonalSucursal, Venta, Item, Cliente, Farmacia, User
from .forms import ItemForm, VentaForm, AñadirStock, ClienteForm, BuscarClienteForm, SalesSearchForm, ReportForm, FarmaciaForm, BuscarProductoForm
from .utils import calcularImporte, controlarStock, get_cliente_por_id, get_farmacia_por_id, get_vendedor_por_id, get_chart, render_to_pdf, controlar_dt
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .decorators import unauthorized_user

import pandas as pd
import datetime
import time

from datetime import timezone

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse


@login_required
def home(request):
    permiso = None
    username = None

    if request.user.is_authenticated:
        username = request.user
        farmacia_personal = PersonalSucursal.objects.get(
            user__username=username).farmacia
        # print(farmacia_personal.id)
        request.session['suc'] = farmacia_personal.id

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
def item_create(request, pk):
    permiso = None
    username = None
    form = ItemForm()

    num_vta = request.session.get('num_vta')
    nombre = request.session.get('prod_name')
    # print(num_vta)

    if request.user.is_authenticated:
        username = request.user
        if controlar_dt(username):
            # print('Controlar_dt')
            permiso = True
            stock = False
            vta = Venta.objects.get(id=num_vta)
            suc = request.session.get('suc')
            print(suc)

            # Se excluyen los productos sin stock
            ItemForm.base_fields['producto'] = forms.ModelChoiceField(
                queryset=Producto.objects.filter(farmacia=suc).exclude(cantidad=0).filter(id=pk))
            producto = Producto.objects.get(id=pk)

            if request.method == 'POST':
                form = ItemForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    print('clean data', cd)
                    cantidad = cd['cantidad']
                    # Controlo que haya stock suficiente
                    if cantidad < producto.cantidad:
                        i = Item(producto=producto, cantidad=cantidad)
                        i.venta = Venta.objects.get(id=num_vta)
                        i.save()

                        if 'crear-otro' in request.POST:
                            print('crear-otro')
                            return redirect('/producto/list/')
                        if 'submitted' in request.POST:
                            print('submitted')
                            calcularImporte(num_vta)
                            messages.success(
                                request, "Items creados con éxito")
                            request.session['num_vta'] = None
                            return redirect('/home/')
                    else:
                        messages.warning(request, "No hay suficiente stock")
                        return redirect('/producto/list/')

            else:
                form = ItemForm()
                if 'stock' in request.GET:
                    stock = False
        else:
            print('No esta autenticado')
            form = ItemForm()
            stock = None
            permiso = False

    context = {
        'form': form,
        'stock': False,
        'permiso': permiso,
        # 'producto': producto.nombre,
    }

    return render(request, 'app/item_create.html', context)


@login_required
def venta_create(request, pk):
    submitted = False
    permiso = None
    username = None

    if request.user.is_authenticated:
        username = request.user

        VentaForm.base_fields['cliente'] = forms.ModelChoiceField(
            queryset=Cliente.objects.filter(id=pk))
        vendedor = PersonalSucursal.objects.get(user__username=username)

        if controlar_dt(username):
            permiso = True
            if request.method == 'POST':
                form = VentaForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    metodo_pago = cd['metodo_pago']
                    cliente = cd['cliente']
                    farmacia = vendedor.farmacia
                    vta = Venta(metodo_pago=metodo_pago,
                                cliente=cliente, vendedor=vendedor, farmacia=farmacia)
                    vta.save()
                    request.session['num_vta'] = str(vta.id)
                    print(vta.id)
                    messages.success(request, "Venta creado con éxito")
                    return redirect('/producto/list/')
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

#### NUEVAS #####


class VentaList(LoginRequiredMixin, ListView):
    model = Venta
    context_object_name = 'Venta'
    template_name = 'app/venta_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['Venta'] = context['Venta'].filter(id=search_input)
        return context


class VentaDetail(LoginRequiredMixin, DetailView):
    model = Venta
    context_object_name = 'Venta'
    template_name = 'app/venta_detail.html'


class VentaUpdate(LoginRequiredMixin, UpdateView):
    model = Venta
    fields = '__all__'
    success_url = reverse_lazy('venta-list')


class VentaDelete(LoginRequiredMixin, DeleteView):
    model = Venta
    context_object_name = 'Venta'
    success_url = reverse_lazy('venta-list')


# Cliente ----------------------------------------------------------------


class ClienteList(LoginRequiredMixin, ListView):
    model = Cliente
    context_object_name = 'Cliente'
    template_name = 'app/cliente_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['Cliente'] = context['Cliente'].filter(
                documento__contains=search_input)
        return context


class ClienteDetail(LoginRequiredMixin, DetailView):
    model = Cliente
    context_object_name = 'Cliente'
    template_name = 'app/cliente_detail.html'


class ClienteCreate(LoginRequiredMixin, CreateView):
    model = Cliente
    fields = '__all__'
    # success_url = reverse_lazy('venta-create')

    def get_success_url(self):
        return reverse('venta-create', kwargs={'pk': self.object.pk})


class ClienteUpdate(LoginRequiredMixin, UpdateView):
    model = Cliente
    fields = '__all__'
    success_url = reverse_lazy('cliente-list')


class ClienteDelete(LoginRequiredMixin, DeleteView):
    model = Cliente
    context_object_name = 'Cliente'
    success_url = reverse_lazy('cliente-list')


# PRODUCTO -----------------------

class ProductoList(LoginRequiredMixin, ListView):
    model = Producto
    context_object_name = 'Producto'
    template_name = 'app/producto_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # clte = self.request.get('clte.id')
        # print(clte)
        user_farmacia = PersonalSucursal.objects.get(user=user).farmacia
        context['Producto'] = Producto.objects.filter(farmacia=user_farmacia)

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['Producto'] = context['Producto'].filter(
                nombre__icontains=search_input)
        return context


class ProductoDetail(LoginRequiredMixin, DetailView):
    model = Producto
    context_object_name = 'Producto'
    template_name = 'app/producto_detail.html'


class ProductoCreate(LoginRequiredMixin, CreateView):
    model = Producto
    fields = '__all__'
    # success_url = reverse_lazy('venta-create')

    def get_success_url(self):
        return reverse('producto-create', kwargs={'pk': self.object.pk})


class ProductoUpdate(LoginRequiredMixin, UpdateView):
    model = Producto
    fields = '__all__'
    success_url = reverse_lazy('producto-list')


class ProductoDelete(LoginRequiredMixin, DeleteView):
    model = Producto
    context_object_name = 'Producto'
    success_url = reverse_lazy('producto-list')
