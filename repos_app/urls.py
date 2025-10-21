from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Role & User ViewSets
router.register(r'roles', views.RoleViewSet, basename='roles')
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'repository', views.RepositoryViewSet, basename='repository')

urlpatterns = [
    path('', include(router.urls)),

    # Role Permissions Retrieve/Update
    path('roles/<uuid:role_id>/permissions/', views.RolePermissionsRetrieveUpdateView.as_view(),name='role-permissions'),
    path('permissions/all/', views.AllPermissionsListView.as_view(), name='all-permissions'),

    # Self user retrieve/update
    path('self/', views.UserSelfRetrieveUpdateView.as_view(), name='user-self'),

    # Self user permissions view
    path('self/permissions/', views.SelfUserPermissionsView.as_view(), name='user-self-permissions'),

    # Invitations list/create
    path('invitations/', views.InvitationListCreateView.as_view(), name='invitations'),
]
