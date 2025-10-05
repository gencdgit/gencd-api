from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'logs', views.LogReadOnlyViewSet)

urlpatterns = [
    
    ###################################################### Migrations ######################################################################

    path('', include(router.urls)),
    path('logs-export/', views.LogCSVExportView.as_view(), name='log-csv-export'),    
]
