from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import DoctorForm, MappingForm, PatientForm, SignupForm
from .models import Doctor, Patient, PatientDoctorMapping


def welcome(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, "Your account is ready. Welcome to CareDesk.")
        return redirect("dashboard")
    return render(request, "api/welcome.html", {"form": form})


def login_page(request):
    from django.contrib.auth.forms import AuthenticationForm

    if request.user.is_authenticated:
        return redirect("dashboard")
    next_url = request.POST.get("next") or request.GET.get("next", "")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("dashboard")
    return render(request, "api/login.html", {"form": form, "next": next_url})


@login_required(login_url="/login/")
def dashboard(request):
    context = {
        "patient_count": Patient.objects.filter(created_by=request.user).count(),
        "doctor_count": Doctor.objects.filter(created_by=request.user).count(),
        "assignment_count": PatientDoctorMapping.objects.filter(patient__created_by=request.user).count(),
        "recent_patients": Patient.objects.filter(created_by=request.user)[:5],
    }
    return render(request, "api/dashboard.html", context)


@login_required(login_url="/login/")
def patients_page(request):
    form = PatientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        patient = form.save(commit=False)
        patient.created_by = request.user
        patient.save()
        messages.success(request, "Patient added.")
        return redirect("patients-page")
    patients = Patient.objects.filter(created_by=request.user)
    return render(request, "api/patients.html", {"form": form, "patients": patients})


@login_required(login_url="/login/")
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
    form = PatientForm(request.POST or None, instance=patient)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Patient details updated.")
        return redirect("patients-page")
    return render(request, "api/edit_record.html", {"form": form, "kind": "patient", "record_name": patient.name})


@login_required(login_url="/login/")
@require_POST
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
    patient.delete()
    messages.success(request, "Patient deleted.")
    return redirect("patients-page")


@login_required(login_url="/login/")
def doctors_page(request):
    form = DoctorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        doctor = form.save(commit=False)
        doctor.created_by = request.user
        doctor.save()
        messages.success(request, "Doctor added.")
        return redirect("doctors-page")
    doctors = Doctor.objects.all()
    return render(request, "api/doctors.html", {"form": form, "doctors": doctors})


@login_required(login_url="/login/")
def doctor_edit(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk, created_by=request.user)
    form = DoctorForm(request.POST or None, instance=doctor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Doctor details updated.")
        return redirect("doctors-page")
    return render(request, "api/edit_record.html", {"form": form, "kind": "doctor", "record_name": doctor.name})


@login_required(login_url="/login/")
@require_POST
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk, created_by=request.user)
    doctor.delete()
    messages.success(request, "Doctor deleted.")
    return redirect("doctors-page")


@login_required(login_url="/login/")
def mappings_page(request):
    form = MappingForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                mapping = form.save(commit=False)
                mapping.assigned_by = request.user
                mapping.save()
            messages.success(request, "Doctor assigned to patient.")
            return redirect("mappings-page")
        except IntegrityError:
            form.add_error("doctor", "This doctor is already assigned to this patient.")
    mappings = PatientDoctorMapping.objects.filter(patient__created_by=request.user).select_related("patient", "doctor")
    return render(request, "api/mappings.html", {"form": form, "mappings": mappings})


@login_required(login_url="/login/")
@require_POST
def mapping_delete(request, pk):
    mapping = get_object_or_404(PatientDoctorMapping, pk=pk, patient__created_by=request.user)
    mapping.delete()
    messages.success(request, "Doctor assignment removed.")
    return redirect("mappings-page")


@login_required(login_url="/login/")
@require_POST
def logout_page(request):
    logout(request)
    return redirect("welcome")
