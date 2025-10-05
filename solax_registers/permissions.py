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
        model1, model2 = view.model, view.last_record_model
        app_name = self._get_app_name(model1)
        has_access_to_model1 = has_user_permission(app_name, model1, action, user)
        has_access_to_model2 = has_user_permission(app_name, model2, action, user)
        return has_access_to_model1 and has_access_to_model2

    def _get_app_name(self, model) -> str:
        """Finds the app name of a given view."""

        return model._meta.app_label

    def has_object_permission(self, request, view, obj):
        return True
