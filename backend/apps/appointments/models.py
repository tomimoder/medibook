import uuid
from django.db import models
from apps.users.models import User
from apps.doctors.models import Doctor
from apps.schedules.models import Schedule


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pendiente'
        CONFIRMED = 'confirmed', 'Confirmada'
        COMPLETED = 'completed', 'Completada'
        CANCELLED = 'cancelled', 'Cancelada'

    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    patient = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'appointments')
    doctor = models.ForeignKey(Doctor, on_delete = models.CASCADE, related_name = 'appointments')
    schedule = models.ForeignKey(Schedule, on_delete = models.CASCADE, related_name = 'appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length = 10, choices = Status.choices, default=Status.PENDING)
    reason = models.TextField(help_text = 'Motivo de la consulta')
    notes = models.TextField(blank = True, help_text = 'Notas del doctor')
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        unique_together = ['doctor', 'date', 'start_time']  # Un doctor no puede tener dos citas al mismo tiempo

    def __abs__(self):
        return f'{self.patient.full_name} con Dr. {self.doctor.user.full_name} - {self.date} {self.start_time}'