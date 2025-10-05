import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter
from extras_app import models, permissions, filters
from extras_app import serializers

###################################################### Logs ######################################################################

class LogReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = models.Log.objects.all()
    serializer_class = serializers.LogSerializer
    permission_slugs = ("logs.list")
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = filters.LogFilter
    ordering_fields = ['timestamp']
    
    

class LogCSVExportView(APIView):
    permission_slugs = ("logs.export")
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.LogFilter

    def get(self, request, *args, **kwargs):
        queryset = models.Log.objects.all()

        # Apply filters manually
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)

        # Prepare CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="logs_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Timestamp', 'User', 'Endpoint', 'Method', 'Status Code', 'Latency',
            'IP Address', 'Service'
        ])

        for log in queryset:
            writer.writerow([
                log.timestamp,
                str(log.user) if log.user else "Anonymous",
                log.endpoint,
                log.http_method,
                log.status_code,
                log.latency,
                log.ip_address,
                log.service
            ])

        return response