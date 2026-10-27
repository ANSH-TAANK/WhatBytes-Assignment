from typing import ClassVar

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Doctor, Patient, PatientDoctorMapping, User
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    DoctorSerializer,
    MappingSerializer,
    PatientSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes: ClassVar[list[type]] = [AllowAny]
    throttle_classes: ClassVar[list[type]] = [ScopedRateThrottle]
    throttle_scope = "register"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes: ClassVar[list[type]] = [AllowAny]
    throttle_classes: ClassVar[list[type]] = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        password = request.data.get("password", "")
        if not email or not password:
            raise ValidationError({"detail": "Email and password are required."})
        try:
            user_record = User.objects.get(email=email)
        except User.DoesNotExist:
            user_record = None
        user = authenticate(request, username=user_record.username, password=password) if user_record else None
        if user is None:
            return Response({"detail": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({"user": UserSerializer(user).data, "access": str(refresh.access_token), "refresh": str(refresh)})


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes: ClassVar[list[type]] = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes: ClassVar[list[type]] = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Doctor.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = MappingSerializer
    permission_classes: ClassVar[list[type]] = [IsAuthenticated]

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(patient__created_by=self.request.user).select_related("patient", "doctor")

    def perform_create(self, serializer):
        patient = serializer.validated_data["patient"]
        if patient.created_by_id != self.request.user.id:
            raise PermissionDenied("You can assign doctors only to your own patients.")
        serializer.save(assigned_by=self.request.user)


class MappingDetailView(APIView):
    permission_classes: ClassVar[list[type]] = [IsAuthenticated]

    def get(self, request, identifier):
        patient = get_object_or_404(Patient, pk=identifier, created_by=request.user)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related("patient", "doctor")
        return Response(MappingSerializer(mappings, many=True).data)

    def delete(self, request, identifier):
        mapping = get_object_or_404(
            PatientDoctorMapping.objects.filter(patient__created_by=request.user), pk=identifier
        )
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
