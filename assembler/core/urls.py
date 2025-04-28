# from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import re_path

from core.views import (
    MachineListView,
    MachineCreateView,
    PartListView,
    PartCreateView,
    AssemblyListView,
    AssemblyCreateView,
    ManageObjectsView,
    SaveAllObjectsView,
)

urlpatterns = [
    re_path(r"^machines/$", MachineListView.as_view(), name="list_machines"),
    re_path(r"^machines/add/$", MachineCreateView.as_view(), name="add_machine"),
    re_path(r"^parts/$", PartListView.as_view(), name="list_parts"),
    re_path(r"^parts/add/$", PartCreateView.as_view(), name="add_part"),
    re_path(r"^assemblies/$", AssemblyListView.as_view(), name="list_assemblies"),
    re_path(r"^assemblies/add/$", AssemblyCreateView.as_view(), name="add_assembly"),
    re_path(r"^manage/$", ManageObjectsView.as_view(), name="manage_objects"),
    re_path(r"^save/$", SaveAllObjectsView.as_view(), name="save_all_objects"),
    re_path(r"^$", RedirectView.as_view(url="/machines/", permanent=True)),
]
