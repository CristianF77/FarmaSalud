from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Producto, Personal, Venta, Item, Cliente
from .forms import ItemForm, VentaForm, AñadirStock, ClienteForm, BuscarClienteForm
from .utils import reducirCantidad, calcularImporte


def home(request):
    venta = Venta.objects.all()
    # Calucalar importe
    context = {
        'venta':venta,
    }
    return render(request, 'app/home.html', context)


def productos_stock(request):
    productos = Producto.objects.all()
    
    if request.method == 'POST':
        print(request.POST['id'])
        redirect('/stock/add/' + request.POST['id'])

    context= {
        'productos': productos,
    }
    return render(request, 'app/stock.html', context)


def personal(request):
    personal = Personal.objects.filter(cargo='DT')
    context = {        
        'personal': personal,
    }
    return render(request, 'app/personal.html', context)


def item_create(request, num_vta):
    submitted = False
    
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            producto = cd['producto']
            cantidad = cd['cantidad']
            if producto.cantidad == 0:
                # Msj no hay stock
                # hay_stock
                pass
            else:
                i = Item(producto=producto, cantidad= cantidad)
                i.venta = Venta.objects.get(id=num_vta)
                i.save()
                reducirCantidad(producto, cantidad)
                if 'crear-otro' in request.POST:
                    return redirect('/venta/' + str(num_vta) + '/item/')
                if 'submitted' in request.POST:
                    calcularImporte(num_vta)
                    return redirect('/home/')
                
                
    else:
        form = ItemForm()
        if 'submitted' in request.GET:
            submitted = True
    
    context = {
        'form': form,
        'submitted': submitted
        }
            
    return render(request, 'app/item_create.html', context)


def venta_create(request):
    submitted = False
    clte_id = request.session.get('clte')
    print(clte_id)
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            metodo = cd['metodo']
            cliente = cd['cliente']
            vendedor = cd['vendedor']
            vta = Venta(metodo_pago=metodo, cliente=cliente, vendedor=vendedor)
            vta.save()
            print(vta.id)
            return HttpResponseRedirect('/venta/' + str(vta.id) + '/item/')
    else:
        form = VentaForm()
        if 'submitted' in request.GET:
            submitted = True
    
    context = {
        'form': form,
        'submitted': submitted
        }
            
    return render(request, 'app/venta_create.html', context)


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
            clte = Cliente(documento=documento, nombre=nombre,apellido=apellido, direccion=direccion, telefono=telefono, email=email, obra_social=obra_social)
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
    
