from .models import Venta, Item
import base64, uuid
from django.core.files.base import ContentFile


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
    _ , str_image = data.split(';base64')
    decoded_img = base64.b64decode(str_image)
    img_name = str(uuid.uuid4())[:10] + '.png'
    data = ContentFile(decoded_img, name=img_name)
    return data