from django.contrib import admin
from .models import Machine, Part, Assembly

admin.site.register(Machine)
admin.site.register(Part)
admin.site.register(Assembly)
