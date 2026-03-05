from django.urls import path
from apps.doctors.views import DoctorListView, DoctorDetailView, DoctorCreateView, SpecialtyListView

urlpatterns = [
    path('',           DoctorListView.as_view(),    name='doctor-list'),
    path('<uuid:pk>/', DoctorDetailView.as_view(),  name='doctor-detail'),
    path('create/',    DoctorCreateView.as_view(),  name='doctor-create'),
]