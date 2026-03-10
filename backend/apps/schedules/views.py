from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.schedules.models import Schedule
from apps.schedules.serializers import ScheduleSerializer, AvailabilitySerializer
from apps.doctors.models import Doctor
from datetime import datetime, timedelta, date
from apps.appointments.models import Appointment

class ScheduleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            doctor = request.user.docotor_profile
            schedules = Schedule.objects.filter(doctor=doctor)
            serializer = ScheduleSerializer(schedules, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Doctor.DoesNotExist:
            return Response({"detail": "El usuario no es un doctor."}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        try:
            doctor = request.user.doctor_profile
        except Exception:
            return Response({'detail': 'No tienes perfil de doctor.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ScheduleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            doctor = request.user.docotr_profile
            schedule = Schedule.objects.get(id=pk, doctor=doctor)
        except Schedule.DoesNotExist:
            return Response({"detail": "Horario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'detail': 'No tienes perfil de doctor.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            doctor = request.user.doctor_profile
            schedule = Schedule.objects.get(id=pk, doctor=doctor)
        except Schedule.DoesNotExist:
            return Response({"detail": "Horario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'detail': 'No tienes perfil de doctor.'}, status=status.HTTP_400_BAD_REQUEST)
        
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class DoctorAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, doctor_id):
        date_param = request.query_params.get('date')
        if not date_param:
            return Response({"detail": "La fecha es requerida."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            query_date = datetime.strptime(date_param, "%Y-%m-%d").date()
            doctor = Doctor.objects.get(id=doctor_id)
        except ValueError:
            return Response({"detail": "Formato de fecha inválido. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        except Doctor.DoesNotExist:
            return Response({"detail": "Doctor no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        day_of_week = query_date.weekday()
        try:
            schedule = Schedule.objects.get(doctor=doctor, day_of_week=day_of_week, is_active=True)
        except Schedule.DoesNotExist:
            return Response({'date': date_param, 'slots': []})
        
        # Obtener slots ya reservados
        reserved = Appointment.objects.filter(
            doctor = doctor,
            date = query_date,
        ).exclude(
            status = Appointment.Status.CANCELLED
        ).values_list('start_time', flat = True)
        
        # Generar los slots disponibles
        slots = []
        current = datetime.combine(query_date, schedule.start_time)
        end = datetime.combine(query_date, schedule.end_time)
        delta = timedelta(minutes=schedule.slot_duration)

        while current + delta <= end:
            if current.time() not in reserved:
                slots.append(current.time().strftime('%H:%M'))
            current += delta

        return Response({'date': date_param, 'slots': slots})
