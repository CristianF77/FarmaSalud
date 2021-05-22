from .models import Venta, Item


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

