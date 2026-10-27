from typing import ClassVar

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Doctor, Patient, PatientDoctorMapping, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Profile", {"fields": ("name",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Profile", {"fields": ("name", "email")}),)
    list_display: ClassVar[list[str]] = ["username", "email", "name", "is_staff"]


admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(PatientDoctorMapping)
