"""The custom permissions file."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .utils import has_user_permission


class HasModelPermission(BasePermission):
    """Checks if a user has permission for a specified action on a custom model."""

    def has_permission(self, request: Request, view):
        if request.method in ("OPTIONS", "HEAD"):
            return True

        MAPPINGS = {"GET": "view", "POST": "add", "DELETE": "delete"}
        action = MAPPINGS[request.method]

        user = request.user
        model = view.serializer_class.Meta.model
        app_name = self._get_app_name(view)

        return has_user_permission(app_name, model, action, user)

    def _get_app_name(self, view) -> str:
        """Finds the app name of a given view."""

        module_segments: str = view.__module__
        return module_segments.split(".")[0]

    def has_object_permission(self, request, view, obj):
        return True
