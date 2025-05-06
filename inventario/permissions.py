from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite acceso de solo lectura a usuarios autenticados,
    y acceso completo (incluyendo la interfaz DRF) solo a superusuarios.
    """

    def has_permission(self, request, view):
        # Si no está autenticado, no tiene acceso a nada
        if not request.user.is_authenticated:
            return False

        # Si es superusuario, acceso total
        if request.user.is_superuser:
            return True

        # Si el método es de solo lectura (GET, HEAD, OPTIONS), se permite
        return request.method in permissions.SAFE_METHODS