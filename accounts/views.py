from django.shortcuts import render
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer, ProfileSerializer, UserProfileSerializer
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User, Profile
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.conf import settings

# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                'message': 'Registration Succssfull',
                'role': user.role,
            }, status=status.HTTP_201_CREATED)
        
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Login successfull',
                "refresh":str(refresh),
                "access":str(refresh.access_token),
                "role": user.role,
            }, status=status.HTTP_200_OK)
            
class UserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        if search:
                return User.objects.filter(role__icontains=search)
        return User.objects.all()
          

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Users found successfully',
            'users': serializer.data
        }, status=status.HTTP_200_OK)
        
class UserListDeleteView(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
   
    def delete(self, request, pk, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({'detail': 'You do not have permission to delete users.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({'detail': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
            

class ProfileView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
        
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response({
            "skill": serializer(profile).data,
            "message": "Uploaded successfully"
        }, status=status.HTTP_201_CREATED)
        
class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        profiles = Profile.objects.all()
        serializer = self.serializer_class(profiles, many=True)
        return Response({
            'profiles': serializer.data
        }, status=status.HTTP_200_OK)
    