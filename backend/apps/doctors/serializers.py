from rest_framework import serializers
from apps.doctors.models import Doctor, Specialty
from apps.users.serializers import UserSerializer

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ['id', 'name', 'description']


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specialty = SpecialtySerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialty', 'license_number', 'bio', 'consultation_fee', 'is_available', 'created_at']


class DoctorCreateSerializer(serializers.ModelSerializer):
    specialty_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Doctor
        fields = ['specialty_id', 'license_number', 'bio', 'consultation_fee']

    def validate_specialty_id(self, value):
        if not Specialty.objects.filter(id=value).exists():
            raise serializers.ValidationError("Especialidad no existe.")
        return value
    
    def create(self, validated_data):
        specialty_id = validated_data.pop('specialty_id')
        specialty = Specialty.objects.get(id=specialty_id)
        doctor = Doctor.objects.create(specialty=specialty, **validated_data)
        return doctor
