from django.contrib import admin
from django.urls import path
from core import views 

urlpatterns = [
    path('machines/', views.list_machines, name='list_machines'), 
    path('machines/add/', views.add_machine, name='add_machine'),  
    path('parts/', views.list_parts, name='list_parts'),  
    path('parts/add/', views.add_part, name='add_part'),  
    path('assemblies/', views.list_assemblies, name='list_assemblies'), 
    path('assemblies/add/', views.add_assembly, name='add_assembly'),  
]
