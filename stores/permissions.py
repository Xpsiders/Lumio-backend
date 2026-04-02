from rest_framework.permissions import BasePermission

class IsSeller(BasePermission):
    message = 'Only sellers can perform this action'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'seller'

class IsApprovedSeller(BasePermission):
    message = 'Your store must be approved to perform this action'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'seller' and
            hasattr(request.user, 'store') and
            request.user.store.is_approved
        )

class IsStoreOwner(BasePermission):
    message = 'You do not own this store'

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user