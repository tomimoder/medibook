from django.urls import path
from apps.appointments.views import (
    AppointmentListCreateView,
    AppointmentDetailView,
    AppointmentCancelView
)

urlpatterns = [
    path('',                AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('<uuid:pk>/',      AppointmentDetailView.as_view(),     name='appointment-detail'),
    path('<uuid:pk>/cancel/', AppointmentCancelView.as_view(),   name='appointment-cancel'),
]