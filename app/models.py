from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group


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
    CARGO = (('Dir', 'Director'), ('CE', 'Comite Ejecutivo'),
             ('DT', 'Directores Técnicos'), ('Aux', 'Auxiliares'))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=20, blank=True, null=True, default=0)
    apellido = models.CharField(max_length=20, blank=True, null=True, default=0)
    legajo = models.CharField(max_length=20, unique=True)
    documento = models.CharField(max_length=20, blank=True, null=True, default=0)
    direccion = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    legajo = models.CharField(max_length=10, blank=True, null=True)
    cargo = models.CharField(max_length=20, choices=CARGO, blank=True, null=True)
    permisos = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)
    

    class Meta:
        abstract = True


class PersonalSucursal(Personal):

    farmacia = models.ForeignKey(
        Farmacia, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.cargo + ' - ' + self.apellido + ' ' + self.nombre

    def save(self, *args, **kwargs):
        self.permisos = Group.objects.get(name='Director Técnico')

        return super().save(*args, **kwargs)


class PersonalEjecutivo(Personal):

    departamento = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.cargo + ' - ' + self.apellido + ' ' + self.nombre

    def save(self, *args, **kwargs):
        self.permisos = Group.objects.get(name='Ejecutivos')

        return super().save(*args, **kwargs)



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
        return str(self.farmacia.num_suc) + ' - ' + self.nombre + ' - ' + str(self.cantidad)


class Venta(models.Model):
    METODO_PAGO = (('Efectivo', 'Contado'), ('Débito',
                   'Tarjeta de débito'), ('Crédito', 'Tarjeta de crédito'))
    fecha = models.DateTimeField(auto_now=True, editable=True)
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
        return str(self.id) + ' - ' + self.cliente.nombre + ' - ' + str(self.importe)

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


class Reportes(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to='app', blank=True)
    remarks = models.TextField()
    # autor = models.ForeignKey(PersonalEjecutivo, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # def get_absolute_url(self):
    #     return reverse('reports:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ('-created',)
