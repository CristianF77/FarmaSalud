from .models import Producto


def reducirCantidad(producto, cantidad):
    producto.cantidad = producto.cantidad - cantidad
    print(producto.cantidad)
    producto.save()
    return