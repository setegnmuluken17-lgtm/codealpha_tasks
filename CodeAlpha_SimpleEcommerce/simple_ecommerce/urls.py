from django.contrib import admin
from django.urls import include, path

from shop.views import AdminAwareLoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", AdminAwareLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("shop.urls")),
]
