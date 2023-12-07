from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

from main import views

urlpatterns = [
    path("", views.MainManager.as_view(), name="home"),
    path("", include("main.urls")),
    path("select2/", include("django_select2.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
