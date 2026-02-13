from rest_framework import serializers

from .models import Photo, Source, Tag, Victim


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = [
            "id",
            "victim",
            "image",
            "caption",
            "photographer_credit",
            "order_index",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = [
            "id",
            "victim",
            "title",
            "url",
            "publisher_name",
            "publication_date",
            "credibility_score",
            "notes",
        ]


class VictimListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Victim
        fields = [
            "id",
            "full_name",
            "native_name",
            "slug",
            "age",
            "date_of_death",
            "city_of_death",
            "province_or_state",
            "country",
            "short_summary",
            "verification_status",
            "confidence_score",
            "tags",
        ]


class VictimDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
    sources = SourceSerializer(many=True, read_only=True)

    class Meta:
        model = Victim
        fields = [
            "id",
            "full_name",
            "native_name",
            "slug",
            "gender",
            "age",
            "date_of_birth",
            "date_of_death",
            "city_of_death",
            "province_or_state",
            "country",
            "biography",
            "short_summary",
            "occupation",
            "education",
            "marital_status",
            "children_count",
            "verification_status",
            "verification_notes",
            "burial_location",
            "social_links",
            "confidence_score",
            "created_at",
            "updated_at",
            "tags",
            "photos",
            "sources",
        ]
        read_only_fields = ["created_at", "updated_at"]
