from django.shortcuts import render
from .serializers import CategorySerializer, SkillSerializer, UpdateSkillSerializer, BookingSerializer, SkillsNestedSerializer
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from .models import Category, Booking, Skill
from rest_framework.exceptions import PermissionDenied
from .paginations import CustomCursorPagination
# Create your views here.

class CategoryView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomCursorPagination  # ✅ add this

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('-id')

    def post(self, request, *args, **kwargs):
        if Category.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "You have already registered a skill."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save(user=request.user)

        return Response({
            'categories': CategorySerializer(category, context={'request': request}).data,
            'message': "Category selected",
        }, status=status.HTTP_201_CREATED)
        
class SkillView(generics.ListCreateAPIView):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # ✅ For files
    pagination_class = CustomCursorPagination  # ✅ add this

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('-id')
    
    def post(self, request, *args, **kwargs):
        if Skill.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "You have already registered a skill."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        skill = serializer.save()
        return Response({
            "skill": SkillSerializer(skill).data,
            "message": "Uploaded successfully"
        }, status=status.HTTP_201_CREATED)

        
class BookView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = CustomCursorPagination  # ✅ add this

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('-id')
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.save(user=request.user)
        return Response({
            "book": BookingSerializer(book).data,
            "message": "Upload successfully",
        }, status=status.HTTP_201_CREATED)
            
class SkillNestedView(generics.ListAPIView):
    serializer_class = SkillsNestedSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        user = self.request.user

        if user.is_authenticated and user.role == 'create':
            # ✅ If logged in → only their own skills
            return Skill.objects.filter(user=user).order_by('-id')
        if user.is_authenticated and user.role == 'offer' or not user.is_authenticated:
            #If logged in => search by param
            qs = Skill.objects.all()
            if search:
                qs = qs.filter(name__icontains=search)
            return qs.order_by('-id')
        return Skill.objects.all().order_by('-id')
            
        
    
class UpdateSkillView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Skill.objects.filter(user=self.request.user)


  
# class VideoCreateView(generics.CreateAPIView):
#     serializer_class = VideoSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]

#     def post(self, request, *args, **kwargs):
#         skill_id = request.data.get('skill')

#         # ⚠️ Make sure a skill ID was passed
#         if not skill_id:
#             return Response(
#                 {"detail": "Skill ID is required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # ⚠️ Make sure the skill exists and belongs to the user
#         try:
#             skill = Skill.objects.get(user=request.user)
#         except Skill.DoesNotExist:
#             return Response(
#                 {"detail": "Skill not found or permission denied."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(user=request.user, skill=skill)

#         return Response({
#             "video": serializer.data,
#             "message": "Video uploaded successfully"
#         }, status=status.HTTP_201_CREATED)

