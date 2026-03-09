import uuid
from django.db import models
from apps.doctors.models import Doctor


class Schedule(models.Model):

    class DayOfWeek(models.IntegerChoices):
        MONDAY    = 0, 'Lunes'
        TUESDAY   = 1, 'Martes'
        WEDNESDAY = 2, 'Miércoles'
        THURSDAY  = 3, 'Jueves'
        FRIDAY    = 4, 'Viernes'
        SATURDAY  = 5, 'Sábado'
        SUNDAY    = 6, 'Domingo'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.IntegerField(default=30, help_text = 'Duración de cada slot en minutos')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        unique_together = ['doctor', 'day_of_week']

    def __str__(self):
        return f'{self.doctor} - {self.get_day_of_week_display()} {self.start_time} - {self.end_time}'
