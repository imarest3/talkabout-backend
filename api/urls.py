# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crea un router
router = DefaultRouter()

# Registra nuestros ViewSets con el router
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'activities', views.ActivityViewSet, basename='activity')
router.register(r'timeslots', views.TimeSlotViewSet, basename='timeslot')
router.register(r'enrollments', views.EnrollmentViewSet, basename='enrollment')

# Las URLs de la API son generadas automáticamente por el router
urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.EdxLoginView.as_view(), name='edx_login'),
]