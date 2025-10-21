from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from rest_framework import views, generics, viewsets, status, response
from auth_app.models import User, Role
from users_app import permissions
from . import serializers
from users_app import models
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.permissions import IsAuthenticated

###################################################################### Role & Permissions Views ######################################################################


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RoleSerializer
    permission_slugs = ("role.list", "role.create", "role.update", "role.delete")
    queryset = Role.objects.all()

    def get_object(self):
        obj = super().get_object()
        if obj.is_system and self.request.method != 'GET':
            raise PermissionDenied("System roles cannot be modified or deleted.")
        return super().get_object()


class RolePermissionsRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.RoleSerializer
    permission_slugs = ("role.permissions.view", "role.permissions.update")
    queryset = Role.objects.all()

    def get_object(self):
        role_id = self.kwargs.get('role_id')
        obj = Role.objects.get(id=role_id)
        if obj.is_system and self.request.method != 'GET':
            raise PermissionDenied("System roles cannot be modified or deleted.")
        return obj
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data.get('permissions', []), status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        return response.Response({'detail': 'Use PATCH method to update permissions.'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        permissions = request.data.get('permissions', [])
        instance.permissions = permissions
        instance.save()
        return response.Response(permissions, status=status.HTTP_200_OK)




class AllPermissionsListView(views.APIView):
    permission_slugs = ("role.permissions.view")
    
    def get(self, request):
        from helper.permissions import all_permissions_list
        return response.Response(all_permissions_list, status=status.HTTP_200_OK)

###################################################################### Self User Views ######################################################################
    
    
class UserSelfRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.UserSelfUpdateSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.UserSerializer
        return super().get_serializer_class()
    

class SelfUserPermissionsView(generics.RetrieveAPIView):
    serializer_class = serializers.RoleSerializer
    queryset = Role.objects.all()
    
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user.role)
        permissions = serializer.data.get('permissions', [])
        return response.Response({'permissions': permissions}, status=status.HTTP_200_OK)


###################################################################### User Views ######################################################################


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['is_active']
    search_fields = ['first_name', 'last_name', 'email']  
    ordering_fields = ['created_at', 'first_name', 'last_name', 'email']
    
    def get_serializer_class(self):
        if self.request.method == 'UPDATE' or self.request.method == 'PATCH':   
            return serializers.UserUpdateSerializer
        return super().get_serializer_class()
        
    def create(self, request, *args, **kwargs):
        return response.Response({'detail': 'User creation is not allowed via this endpoint. Please use the invitation system.'}, status=status.HTTP_403_FORBIDDEN)

    @transaction.atomic
    def perform_destroy(self, instance):
        models.Invitation.objects.filter(to_email=instance.email).delete()
        super().perform_destroy(instance)
           
    
###################################################################### Invitations ######################################################################

class InvitationListCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.InvitationSerializer
    permission_slugs = ("invitations.list", "invitations.create")
    queryset = models.Invitation.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(from_email = None)
        


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)