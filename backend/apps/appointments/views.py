from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from apps.appointments.models import Appointment
from apps.appointments.serializers import (
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentStatusSerializer
)


class AppointmentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if hasattr(user, 'doctor_profile'):
            appointments = Appointment.objects.filter(doctor = user.doctor_profile).select_related('patient', 'doctor__user', 'doctor__specialty')
        else:
            appointments = Appointment.objects.filter(patient = user.doctor_profile).select_related('patient', 'doctor__user', 'doctor__specialty')

        serializer = AppointmentSerializer(appointments, many = True)
        return Response(serializer.data)
    

    def post(self, request):
        serializer = AppointmentCreateSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data

        try:
            with transaction.atomic():
                # Verficamos si el slot ya está reservado (con bloqueo)
                existing = Appointment.objects.select_for_update().filter(
                    doctor = data['doctor'],
                    date = data['date'],
                    start_time = data['start_time']
                ).exclude(status = Appointment.Status.CANCELLED)

                if existing.exists():
                    return Response({'detail': 'Este horario ya está reservado'},
                    status = status.HTTP_400_BAD_REQUEST
                    )

                appointment = Appointment.objects.create(
                    patient    = request.user,
                    doctor     = data['doctor'],
                    schedule   = data['schedule'],
                    date       = data['date'],
                    start_time = data['start_time'],
                    end_time   = data['end_time'],
                    reason     = data['reason'],
                )

            return Response(
                AppointmentSerializer(appointment).data,
                status = status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response({'detail': str(e)}, status = status.HTTP_400_BAD_REQUEST)

class AppointmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            appointment = Appointment.objects.select_related('patient', 'doctor__user', 'doctor__specialty').get(id = pk)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Cita no encontrada'}, status = status.HTTP_404_NOT_FOUND)
        
        # Solo el paciente o el doctor pueden ver la cita
        if request.user != appointment.patient and not hasattr(request.user, 'doctor_profile'):
            return Response({'detail': 'No tienes permiso para ver esta cita'})
        
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        try:
            appointment = Appointment.objects.get(id = pk)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Cita no encontrada'}, status = status.HTTP_404_NOT_FOUND)

        # Solo el doctor puede cambiar el estado
        if not hasattr(request.user, 'doctor_profile'):
            return Response({'detail': 'No tienes permiso para modificar esta cita'}, status = status.HTTP_403_FORBIDDEN)
        
        serializer = AppointmentStatusSerializer(appointment, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(AppointmentSerializer(appointment).data)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class AppointmentCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(id = pk, patient = request.user)

        except Appointment.DoesNotExist:
            return Response({'detail': 'Cita no encontrada'}, status = status.HTTP_404_NOT_FOUND)
        
        if appointment.status in [Appointment.Status.COMPLETED, Appointment.Status.CANCELLED]:
            return Response(
                {'detail': 'No se puede cancelar una cita completada o ya cancelada'},
                status = status.HTTP_400_BAD_REQUEST
            )

        appointment.status = Appointment.Status.CANCELED
        appointment.save()
        return Response({'detail': 'Cita cancelada correctamente'})
        
