from rest_framework import permissions


class AdminOnlyPermission(permissions.BasePermission):
    """Полные права на управление всем контентом проекта"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_superuser
        )


class AdminOrReadOnlyPermission(permissions.BasePermission):
    """Админ может создавать и удалять произведения, категории и жанры.
     Может назначать роли пользователям. В остальном - только для чтения.
     """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class AuthorModeratorAdminPermission(permissions.BasePermission):
    """Только авторы, модераторы или администраторы
    отзывов/комментов могут ими управлять.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsOwnerOrReadOnlyOrOfficial(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role in ('admin', 'moderator')
            or obj.author == request.user)
