from django.db import models


class Farmacia(models.Model):
    num_suc = models.CharField(max_length=10, blank=True, null=True)
    nombre = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.num_suc + ' - ' + self.direccion


class Cliente(models.Model):
    documento = models.CharField(
        max_length=20, blank=True, null=True, default=0)
    nombre = models.CharField(max_length=20, blank=True, null=True)
    apellido = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=40, blank=True, null=True)
    obra_social = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return (self.nombre + ' ' + self.apellido)


class Personal(models.Model):

    documento = models.CharField(
        max_length=20, blank=True, null=True, default=0)
    nombre = models.CharField(max_length=20, blank=True, null=True)
    apellido = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    legajo = models.CharField(max_length=10, blank=True, null=True)
    # cargo = models.CharField(
    #     max_length=20, choices=CARGO, blank=True, null=True)
    # sucursal, para saber de que farmacia vamos a reducir el stock del producto
    # farmacia = models.ForeignKey(
    #     Farmacia, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        abstract = True


class PersonalSucursal(Personal):
    CARGO = (('Dir', 'Director'), ('CE', 'Comite Ejecutivo'),
             ('DT', 'Directores Técnicos'), ('Aux', 'Auxiliares'))

    cargo = models.CharField(
        max_length=20, choices=CARGO, blank=True, null=True)
    farmacia = models.ForeignKey(
        Farmacia, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.cargo + ' - ' + self.apellido + ' ' + self.nombre


# class PersonalEjecutivas(Personal):
#     pass


class Producto(models.Model):
    TIPO_REMEDIO = (('Libre', 'Venta Libre'), ('Receta', 'Venta con Receta'))
    nombre = models.CharField(max_length=50, blank=True, null=True)
    codigo_barras = models.IntegerField(blank=True, null=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    cantidad = models.IntegerField(blank=True, null=True, default=0)
    venta_Libre = models.CharField(
        max_length=20, choices=TIPO_REMEDIO, blank=True, null=True)
    farmacia = models.ForeignKey(
        Farmacia, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.farmacia.num_suc) + ' - ' + self.nombre


class Venta(models.Model):
    METODO_PAGO = (('Efectivo', 'Contado'), ('Débito',
                   'Tarjeta de débito'), ('Crédito', 'Tarjeta de crédito'))
    fecha = models.DateTimeField(auto_now=True)
    importe = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    metodo_pago = models.CharField(
        choices=METODO_PAGO, max_length=10, blank=True, null=True)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, blank=True, null=True)
    vendedor = models.ForeignKey(
        PersonalSucursal, on_delete=models.SET_NULL, blank=True, null=True)
    farmacia = models.ForeignKey(
        Farmacia, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        total = 0
        for i in Item.objects.filter(venta=self.id):
            total += i.importe
        self.importe = total

        self.farmacia = self.vendedor.farmacia

        return super().save(*args, **kwargs)


# https://medium.com/django-rest/one-to-many-relationship-foreignkey-64f8da35912a
class Item(models.Model):
    venta = models.ForeignKey(
        Venta, on_delete=models.SET_NULL, blank=True, null=True)
    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, blank=True, null=True)
    cantidad = models.IntegerField(blank=True, null=True, default=0)
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    importe = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return 'Item: ' + self.producto.nombre + ' - Cantidad: ' + str(self.cantidad) + ' Precio: ' + str(self.precio) + ' - Importe: ' + str(self.importe)

    def save(self, *args, **kwargs):
        self.precio = self.producto.precio
        self.importe = self.producto.precio * self.cantidad
        return super().save(*args, **kwargs)
