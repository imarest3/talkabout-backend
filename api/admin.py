# api/admin.py

from django.contrib import admin
from .models import User, Activity, ActivityFile, TimeSlot, Enrollment
from django.contrib.auth.admin import UserAdmin


# Creamos una clase de Admin especial para nuestro modelo User
class CustomUserAdmin(UserAdmin):
    """
    Configuración del panel de admin para nuestro User personalizado.
    """
    # Muestra estos campos en la lista de usuarios
    list_display = ('username', 'email', 'edx_user_id', 'is_staff', 'is_active')
    # Añade 'is_staff' a los filtros de la derecha
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    # Configura los campos de búsqueda
    search_fields = ('username', 'email', 'edx_user_id')
    
    # Esto usa los formularios de 'UserAdmin' que saben
    # cómo hashear contraseñas, en lugar de un formulario genérico.
    fieldsets = UserAdmin.fieldsets + (
        ('Campos Personalizados', {'fields': ('edx_user_id', 'timezone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Campos Personalizados', {'fields': ('edx_user_id', 'timezone')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Activity)
admin.site.register(ActivityFile)
admin.site.register(TimeSlot)
admin.site.register(Enrollment)