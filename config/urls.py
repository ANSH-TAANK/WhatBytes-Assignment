from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy

from api import pages

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
    path("register/", pages.welcome, name="register-page"),
    path("login/", pages.login_page, name="login-page"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="api/password_reset_form.html",
            email_template_name="api/password_reset_email.txt",
            subject_template_name="api/password_reset_subject.txt",
            success_url=reverse_lazy("password-reset-done"),
        ),
        name="password-reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="api/password_reset_done.html"),
        name="password-reset-done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="api/password_reset_confirm.html",
            success_url=reverse_lazy("password-reset-complete"),
        ),
        name="password-reset-confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="api/password_reset_complete.html"),
        name="password-reset-complete",
    ),
    path("patients/", pages.patients_page, name="patients-page"),
    path("patients/<int:pk>/edit/", pages.patient_edit, name="patient-edit"),
    path("patients/<int:pk>/delete/", pages.patient_delete, name="patient-delete"),
    path("doctors/", pages.doctors_page, name="doctors-page"),
    path("doctors/<int:pk>/edit/", pages.doctor_edit, name="doctor-edit"),
    path("doctors/<int:pk>/delete/", pages.doctor_delete, name="doctor-delete"),
    path("assignments/", pages.mappings_page, name="mappings-page"),
    path("assignments/<int:pk>/remove/", pages.mapping_delete, name="mapping-delete"),
    path("logout/", pages.logout_page, name="logout-page"),
    path("dashboard/", pages.dashboard, name="dashboard"),
    path("", pages.welcome, name="welcome"),
]
