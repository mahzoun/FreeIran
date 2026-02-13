from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api import PhotoViewSet, SourceViewSet, TagViewSet, VictimViewSet
from .views import name_suggest

router = DefaultRouter()
router.register(r"victims", VictimViewSet, basename="victim")
router.register(r"photos", PhotoViewSet, basename="photo")
router.register(r"sources", SourceViewSet, basename="source")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/suggest/", name_suggest, name="name_suggest"),
]
