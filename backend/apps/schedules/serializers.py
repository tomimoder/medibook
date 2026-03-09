from rest_framework import serializers
from apps.schedules.models import Schedule
from datetime import datetime, timedelta


class ScheduleSerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only = True)
    
    class Meta:
        model = Schedule
        fields = ['id', 'doctor', 'day_of_week', 'day_of_week_display', 'start_time', 'end_time', 'slot_duration', 'is_active', 'created_at']
        read_only_fields = ['doctor']

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError("La hora de inicio debe ser anterior a la hora de fin.")
        return attrs
    

class AvailabilitySerializer(serializers.Serializer):
    date = serializers.DateField()
    slots = serializers.ListField(child=serializers.TimeField())