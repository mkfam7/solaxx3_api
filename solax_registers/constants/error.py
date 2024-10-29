from rest_framework import status
from rest_framework.response import Response

MISSING_FIELDS = Response(
    {"detail": "Query parameter 'fields' is mandatory."},
    status.HTTP_400_BAD_REQUEST,
)

extra_fields_passed = lambda f: Response(
    {"Some extra fields were passed:": f},
    status.HTTP_400_BAD_REQUEST,
)

INVALID_FORCE_PARAM = Response(
    {"detail": "'overwrite' parameter must be either 'true' or 'false'"},
    status.HTTP_400_BAD_REQUEST,
)
MISSING_ACTION_PARAM = Response(
    {"detail": "Non-null query parameter 'action' is mandatory."},
    status.HTTP_400_BAD_REQUEST,
)
INVALID_ACTION_PARAM = Response(
    {"detail": "The value for query parameter 'action' is not among valid actions."},
    status.HTTP_400_BAD_REQUEST,
)
MISSING_DATE_ARG = Response(
    {"detail": "Argument 'date' in 'args' (position 0) is mandatory."},
    status.HTTP_400_BAD_REQUEST,
)
deleted = lambda no_deleted: Response({"deleted": no_deleted}, status.HTTP_200_OK)
