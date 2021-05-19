from .models import Venta, Item


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
