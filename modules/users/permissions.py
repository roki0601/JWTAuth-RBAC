from rest_framework import permissions
from .models import AccessRule, BusinessElement

class RoleBasedPermission(permissions.BasePermission):
    """View должен устанавливать view.element_name и view.action (например 'orders', 'read')"""

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user:
            return False
        element_name = getattr(view, 'element_name', None)
        action = getattr(view, 'action', None)
        if not element_name or not action:
            return True
        element = BusinessElement.objects.filter(name=element_name).first()
        if not element:
            return False
        role = user.role
        if not role:
            return False
        rule = AccessRule.objects.filter(role=role, element=element).first()
        if not rule:
            return False
        mapping = {
            'read': 'read',
            'read_all': 'read_all',
            'create': 'create',
            'update': 'update',
            'update_all': 'update_all',
            'delete': 'delete',
            'delete_all': 'delete_all',
        }
        field = mapping.get(action)
        if not field:
            return False
        return getattr(rule, field, False)
