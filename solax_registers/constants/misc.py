from rest_framework import status
from rest_framework.response import Response

deleted = lambda no_deleted: Response({"deleted": no_deleted}, status.HTTP_200_OK)
