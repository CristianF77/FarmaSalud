from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Farmacia)
admin.site.register(Cliente)
admin.site.register(PersonalSucursal)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(Item)
# admin.site.register(PersonalEjecutivo, UserAdmin)
