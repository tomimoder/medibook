from rest_framework import serializers
from apps.appointments.models import Appointment
from apps.doctors.serializers import DoctorSerializer
from apps.users.serializers import UserSerializer
from datetime import datetime, timedelta

class AppointmentSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only = True)
    doctor = DoctorSerializer(read_only = True)
    status_display = serializers.CharField(source = 'get_status_display', read_only = True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'date', 'start_time', 'end_time', 'status', 'status_display', 'reason', 'notes', 'created_at']


class AppointmentCreateSerializer(serializers.Serializer):
    doctor_id  = serializers.UUIDField()
    date       = serializers.DateField()
    start_time = serializers.TimeField()
    reason     = serializers.CharField()

    def validate(self, attrs):
        from apps.doctors.models import Doctor
        from apps.schedules.models import Schedule

        # Verificar que el doctor existe
        try:
            doctor = Doctor.objects.get(id=attrs.get('doctor_id'))
        except Doctor.DoesNotExist:
            raise serializers.ValidationError({'doctor_id': 'Doctor no encontrado'})

        # Verificar que el día tiene horario activo
        day_of_week = attrs.get('date').weekday()
        try:
            schedule = Schedule.objects.get(doctor=doctor, day_of_week=day_of_week, is_active=True)
        except Schedule.DoesNotExist:
            raise serializers.ValidationError({'date': 'El doctor no tiene horario para este día'})

        # Calcular end_time
        end_time = (datetime.combine(attrs.get('date'), attrs.get('start_time')) +
                    timedelta(minutes=schedule.slot_duration)).time()

        attrs['doctor']   = doctor
        attrs['schedule'] = schedule
        attrs['end_time'] = end_time
        return attrs
    

class AppointmentStatusSerializer(serializers.Serializer):
    class Meta:
        model  = Appointment
        fields = ['status', 'notes']