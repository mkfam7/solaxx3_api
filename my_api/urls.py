"""
URL configuration for my_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from solax_registers.views import Healthz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("rest_framework.urls"), name="api"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger_docs",
    ),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", include("solax_registers.urls")),
    path("healthz", Healthz.as_view(), name="healthz"),
]
