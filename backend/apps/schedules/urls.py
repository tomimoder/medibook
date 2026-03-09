from django.urls import path
from apps.schedules.views import ScheduleListCreateView, ScheduleDetailView, DoctorAvailabilityView

urlpatterns = [
    path('',                                    ScheduleListCreateView.as_view(), name='schedule-list-create'),
    path('<uuid:pk>/',                          ScheduleDetailView.as_view(),     name='schedule-detail'),
    path('availability/<uuid:doctor_id>/',      DoctorAvailabilityView.as_view(), name='doctor-availability'),
]