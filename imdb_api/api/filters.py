from django_filters import rest_framework as filters
from .models import Title


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class TitleFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    year = filters.NumberFilter()
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact')
    genre = CharFilterInFilter(field_name='genre__slug', lookup_expr='in')

    class Meta:
        models = Title
        fields = ['category', 'year', 'name', 'genre']
