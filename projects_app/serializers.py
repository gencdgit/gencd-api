from django.db import transaction
from rest_framework import serializers
from users_app import models
from helper.utils import encode_token
from helper.exceptions import SmoothException
from auth_app.models import User, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = User
        exclude = ['password', 'profile_picture']

        
class UserSelfUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only = True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'profile_picture']
        

class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only = True)
    
    class Meta:
        model = User
        fields = ['id', 'role']
                
    
class InvitationSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()    
    token = serializers.CharField(write_only=True, required=False)
    role_id = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = models.Invitation
        fields = '__all__'

    def create(self, validated_data):
        from_email = validated_data.get('from_email')
        to_email = validated_data.get('to_email')
        access_url = validated_data.get('access_url')
        token = encode_token({"role_id": validated_data.get('role_id')})
        
        if User.objects.filter(email=to_email).exists():
            raise SmoothException.error(
                detail=f"A user with this email address already exists.",
                dev_message=f"Attempted to invite an existing user: {to_email}",
            )
        
        invitation = models.Invitation.objects.create(from_email=from_email, to_email=to_email, access_url = access_url, token=token)
        return invitation
