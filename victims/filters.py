import django_filters

from .models import Victim


class VictimFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name="city_of_death", lookup_expr="icontains")
    province = django_filters.CharFilter(
        field_name="province_or_state", lookup_expr="icontains"
    )
    country = django_filters.CharFilter(field_name="country", lookup_expr="icontains")
    verification_status = django_filters.CharFilter(
        field_name="verification_status", lookup_expr="iexact"
    )
    age_min = django_filters.NumberFilter(field_name="age", lookup_expr="gte")
    age_max = django_filters.NumberFilter(field_name="age", lookup_expr="lte")
    tag = django_filters.CharFilter(field_name="tags__slug", lookup_expr="iexact")

    class Meta:
        model = Victim
        fields = [
            "city",
            "province",
            "country",
            "verification_status",
            "age_min",
            "age_max",
            "tag",
        ]
