from .models import Venta, Item, PersonalSucursal, Farmacia, Cliente
import base64
import uuid
from django.core.files.base import ContentFile
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns


def controlarStock(producto, cantidad):
    if producto.cantidad != 0:
        aux = producto.cantidad - cantidad
    elif aux >= 0:
        producto.cantidad = producto.cantidad - cantidad
        print(producto.cantidad)
        producto.save()
        return True
    else:
        return False


def reducirCantidad(producto, cantidad):

    producto.cantidad = producto.cantidad - cantidad
    print(producto.cantidad)
    producto.save()
    return


def calcularImporte(num_vta):
    vta = Venta.objects.get(id=num_vta)
    items = Item.objects.filter(venta=vta.id)
    total = 0
    for i in items:
        total += i.importe

    print(total)
    vta.importe = total
    vta.save()

    return


def get_report_image(data):
    _, str_image = data.split(';base64')
    decoded_img = base64.b64decode(str_image)
    img_name = str(uuid.uuid4())[:10] + '.png'
    data = ContentFile(decoded_img, name=img_name)
    return data


def get_vendedor_por_id(val):
    vendedor = PersonalSucursal.objects.get(id=val)
    vend = vendedor.nombre + ' ' + vendedor.apellido
    return vend


def get_cliente_por_id(val):
    vendedor = Cliente.objects.get(id=val)
    return vendedor


def get_farmacia_por_id(val):
    farmacia = Farmacia.objects.get(id=val)
    farmacia = farmacia.num_suc
    return farmacia


def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def get_key(res_by):
    if res_by == '#1':
        key = 'farmacia'
    elif res_by == '#2':
        key = 'fecha'
    return key


def get_chart(chart_type, data, results_by, **kwargs):
    plt.switch_backend('AGG')
    fig = plt.figure(figsize=(10, 4))
    key = get_key(results_by)
    d = data.groupby(key, as_index=False)['importe'].agg('sum')
    if chart_type == '#1':
        # print('bar chart')
        sns.barplot(x=key, y='importe', data=d)
    elif chart_type == '#2':
        # print('pie chart')
        plt.pie(data=d, x='importe', labels=d[key].values)
    elif chart_type == '#3':
        # print('line chart')
        plt.plot(d[key], d['importe'], color='green',
                 marker='o', linestyle='dashed')
    else:
        print('ups... failed to identify the chart type')
    plt.tight_layout()
    chart = get_graph()
    return chart

