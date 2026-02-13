from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from .filters import VictimFilter
from .models import Photo, Source, Tag, Victim
from .serializers import (
    PhotoSerializer,
    SourceSerializer,
    TagSerializer,
    VictimDetailSerializer,
    VictimListSerializer,
)


class VictimViewSet(viewsets.ModelViewSet):
    queryset = Victim.objects.all().prefetch_related("photos", "sources", "tags")
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    filterset_class = VictimFilter
    search_fields = ["full_name", "native_name", "biography", "short_summary"]
    ordering_fields = ["full_name", "date_of_death", "age", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return VictimListSerializer
        return VictimDetailSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.select_related("victim")
    serializer_class = PhotoSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.select_related("victim")
    serializer_class = SourceSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
