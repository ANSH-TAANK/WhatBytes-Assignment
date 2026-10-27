from typing import ClassVar

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Doctor, Patient, PatientDoctorMapping, User


class SignupForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "The passwords do not match.")
        if password:
            user = User(name=cleaned_data.get("name", ""), email=cleaned_data.get("email", ""))
            try:
                validate_password(password, user=user)
            except ValidationError as error:
                self.add_error("password", error)
        return cleaned_data

    def save(self):
        email = self.cleaned_data["email"]
        return User.objects.create_user(
            username=email,
            email=email,
            name=self.cleaned_data["name"],
            password=self.cleaned_data["password"],
        )


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields: ClassVar[list[str]] = ["name", "age", "gender", "address", "phone"]
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields: ClassVar[list[str]] = ["name", "specialization", "email", "phone", "address"]
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_email(self):
        return self.cleaned_data["email"].lower()


class MappingForm(forms.ModelForm):
    class Meta:
        model = PatientDoctorMapping
        fields: ClassVar[list[str]] = ["patient", "doctor"]

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.filter(created_by=user)
        self.fields["doctor"].queryset = Doctor.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get("patient")
        doctor = cleaned_data.get("doctor")
        if patient and doctor and PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            self.add_error("doctor", "This doctor is already assigned to this patient.")
        return cleaned_data
