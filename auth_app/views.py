from rest_framework import views, generics, status, response
from . import serializers
from auth_app import models
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from helper.utils import delete_session


class RegisterView(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer
    queryset = models.User.objects.all()
    authentication_classes = []
    permission_classes = [AllowAny]
    
    
class LoginView(views.APIView):
    serializer_class = serializers.LoginSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        login_data = serializer.validated_data
        return response.Response(login_data, status=status.HTTP_200_OK)
     

class LogoutView(views.APIView):
    
    def post(self, request):
        session_key = request.decoded_payload.get('session_key')
        if session_key:
            delete_session(session_key)
        return response.Response({'detail' : "Successfully logged out"}, status=status.HTTP_200_OK)


class ChangePasswordView(views.APIView):
    serializer_class = serializers.ChangePasswordSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return response.Response({'detail' : "Password changed successfully"}, status=status.HTTP_200_OK)
     
     
class PasswordResetRequestView(views.APIView):
    serializer_class = serializers.PasswordResetRequestSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return response.Response({'detail' : "Password reset link sent to your email"}, status=status.HTTP_200_OK)
     
     
class PasswordResetView(views.APIView):
    serializer_class = serializers.PasswordResetSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context = {'request': request})
        serializer.is_valid(raise_exception=True)
        return response.Response({'detail' : "Password Reset successfully"}, status=status.HTTP_200_OK)
     
 
class SocialLoginView(views.APIView):
    serializer_class = serializers.SocialLoginSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        login_data = serializer.validated_data
        return response.Response(login_data, status=status.HTTP_200_OK)