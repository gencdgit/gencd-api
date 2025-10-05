from django_filters import rest_framework as filters
from extras_app import models

class LogFilter(filters.FilterSet):
    _from = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    _to = filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = models.Log
        fields = ['user', 'http_method', 'status_code', 'ip_address', 'service', '_from', '_to']
