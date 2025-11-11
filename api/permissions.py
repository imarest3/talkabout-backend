# api/permissions.py

from rest_framework import permissions
from zoneinfo import ZoneInfo



class IsAdminUser(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a administradores (superusers).
    """
    def has_permission(self, request, view):
        # request.user.is_authenticated es para asegurar que el usuario está logueado
        return request.user and request.user.is_authenticated and request.user.is_superuser

class IsStaffUser(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a personal (profesores) o administradores.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

class IsOwnerOrStaffReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para objetos (Actividades, Convocatorias):
    - Todos pueden LEER (GET, HEAD, OPTIONS).
    - Solo el 'dueño' (owner) o 'staff' (profesor/admin) puede ESCRIBIR (POST, PUT, DELETE).
    """
    def has_permission(self, request, view):
        # Si el método es seguro (GET, etc.), permite a cualquiera.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Si el método es de escritura (POST, PUT), solo permite a staff/admin.
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        # Si el método es seguro (GET), permite a todos.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Si el método es de escritura (PUT, DELETE),
        # solo permite si el usuario es el 'dueño' del objeto O un admin.
        return obj.owner == request.user or request.user.is_superuser