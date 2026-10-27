from typing import ClassVar

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Doctor, Patient, PatientDoctorMapping, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields: ClassVar[list[str]] = ["id", "name", "email"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields: ClassVar[list[str]] = ["id", "name", "email", "password"]

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized

    def create(self, validated_data):
        email = validated_data["email"]
        username = email
        return User.objects.create_user(username=username, email=email, **{k: v for k, v in validated_data.items() if k != "email"})


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields: ClassVar[list[str]] = ["id", "name", "age", "gender", "address", "phone", "created_at", "updated_at"]
        read_only_fields: ClassVar[list[str]] = ["id", "created_at", "updated_at"]

    def validate_age(self, value):
        if value > 120:
            raise serializers.ValidationError("Age must be 120 or below.")
        return value


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields: ClassVar[list[str]] = ["id", "name", "specialization", "email", "phone", "address", "created_at", "updated_at"]
        read_only_fields: ClassVar[list[str]] = ["id", "created_at", "updated_at"]

    def validate_email(self, value):
        return value.lower()


class MappingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields: ClassVar[list[str]] = ["id", "patient", "patient_name", "doctor", "doctor_name", "created_at"]
        read_only_fields: ClassVar[list[str]] = ["id", "patient_name", "doctor_name", "created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["patient"].queryset = Patient.objects.filter(created_by=request.user)

    def validate(self, attrs):
        patient = attrs.get("patient", getattr(self.instance, "patient", None))
        doctor = attrs.get("doctor", getattr(self.instance, "doctor", None))
        if patient and doctor:
            assignments = PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor)
            if self.instance:
                assignments = assignments.exclude(pk=self.instance.pk)
            if assignments.exists():
                raise serializers.ValidationError({"doctor": "This doctor is already assigned to the patient."})
        return attrs
