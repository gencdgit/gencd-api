
from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('auth_app.urls')),
    path('api/user/', include('users_app.urls')),
    path('api/user/', include('extras_app.urls')),
]
