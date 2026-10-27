from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    DoctorViewSet,
    LoginView,
    MappingDetailView,
    MappingListCreateView,
    PatientViewSet,
    RegisterView,
)

router = DefaultRouter()
router.register("patients", PatientViewSet, basename="patient")
router.register("doctors", DoctorViewSet, basename="doctor")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("mappings/", MappingListCreateView.as_view(), name="mapping-list-create"),
    path("mappings/<int:identifier>/", MappingDetailView.as_view(), name="mapping-detail"),
    path("", include(router.urls)),
]
