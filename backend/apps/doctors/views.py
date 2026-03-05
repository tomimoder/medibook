from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.doctors.models import Doctor, Specialty
from apps.doctors.serializers import DoctorSerializer, DoctorCreateSerializer, SpecialtySerializer

class SpecialtyListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        specialties = Specialty.objects.all()
        serializer = SpecialtySerializer(specialties, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SpecialtySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DoctorListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        doctors = Doctor.objects.filter(is_available=True).select_related('user', 'specialty')
        specialty = request.query_params.get('specialty')
        if specialty:
            doctors = doctors.filter(specialty__name__icontains=specialty)
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)
    

class DoctorDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            doctor = Doctor.objects.select_related('user', 'specialty').get(id=pk)
            serializer = DoctorSerializer(doctor)
            return Response(serializer.data)
        except Doctor.DoesNotExist:
            return Response({"detail": "Doctor no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        

class DoctorCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'doctor_profile'):
            return Response({'detail': 'Este usuario ya tiene un perfil de doctor'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DoctorCreateSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save(user=request.user)
            return Response(DoctorSerializer(doctor).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)