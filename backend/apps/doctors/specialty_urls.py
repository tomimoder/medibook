from django.urls import path
from apps.doctors.views import SpecialtyListView

urlpatterns = [
    path('', SpecialtyListView.as_view(), name='specialty-list'),
]