
from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('auth_app.urls')),
    path('api/user/', include('users_app.urls')),
    path('api/user/', include('extras_app.urls')),

    path('api/projects/', include('projects_app.urls')),
    path('api/repositories/', include('repos_app.urls')),
]
