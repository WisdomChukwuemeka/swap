from rest_framework import serializers
from .models import Category, Skill, Booking, Video
import os
# import mimetypes




# class VideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Video
#         fields = [
#             "id",
#             "file",
#             "title",
#             "description",
#         ]
#         read_only_fields = ["id"]

#     def validate_file(self, value):
#         print("DEBUG FILE:", value, "TYPE:", type(value))

#         if value in [None, ""]:
#             return None  # Allow empty

#         if not hasattr(value, "size"):
#             raise serializers.ValidationError("Invalid file type.")

#         if not isinstance(value.size, int):
#             raise serializers.ValidationError("File size must be int.")

#         if value.size < 2 * 1024 * 1024:
#             raise serializers.ValidationError("Video too small (min 2MB).")

#         if value.size > 100 * 1024 * 1024:
#             raise serializers.ValidationError("Video too big (max 100MB).")

#         # ✅ Check the file extension
#         valid_extensions = [".mp4", ".mov", ".avi", ".mkv"]
#         ext = os.path.splitext(value.name)[1].lower()
#         if ext not in valid_extensions:
#             raise serializers.ValidationError(
#                 f"Unsupported file extension '{ext}'. Allowed: {valid_extensions}"
#             )
#         return value





class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id',
            'skill',
            'note',
            'booking_date',
            'status',
            'created_at',
            'booking_user'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'booking_user']
        

    def create(self, validated_data):
        validated_data['booking_user'] = self.context['request'].user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'category_name',
            'user',
        ]
        read_only_fields = ['id', 'user']
        
class VideoSerializer(serializers.ModelSerializer):
    video_file = serializers.SerializerMethodField()
    class Meta:
        model = Video
        fields = ['id', 'video_file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
        
    def get_video_file(self, obj):
        request = self.context.get('request')
        if obj.video_file and hasattr(obj.video_file, 'url'):
            media_url = obj.video_file.url.replace('/media/', '/api/media/')
            return request.build_absolute_uri(media_url)
        return None

    def validate_video_file(self, value):
        ext = value.name.split('.')[-1].lower()
        if ext not in ['mp4', 'mov', 'avi', 'mkv']:
            raise serializers.ValidationError("Only mp4, mov, avi, mkv allowed.")
        if value.size < 2 * 1024 * 1024:
            raise serializers.ValidationError("File too small (min 2 MB).")
        if value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError("File too large (max 100 MB).")
        return value
        
class SkillSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(write_only=True)
    video_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Skill
        fields = [
            'id',
            'category_name',
            'profile_image',
            'full_name',
            'bio',
            'certificate',
            'experience',
            'skills',
            'created_at',
            'video_file'
        ]
        read_only_fields = ['id', 'created_at']

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        # 👇 decode JSON array if needed
        skills = data.get('skills')
        if isinstance(skills, str):
            import json
            try:
                data['skills'] = ', '.join(json.loads(skills))
            except Exception:
                pass
        return data

    def create(self, validated_data):
        category_name = validated_data.pop('category_name')
        video_file = validated_data.pop('video_file', None)
        user = self.context['request'].user

        category, _ = Category.objects.get_or_create(
            user=user,
            category_name=category_name
        )

        skill = Skill.objects.create(
            category=category,
            user=user,
            **validated_data
        )

        # ✅ Now attach the video if present
        if video_file:
            Video.objects.create(
                skill=skill,
                user=user,
                video_file=video_file
            )

        return skill

    

class SkillsNestedSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    profile_image = serializers.SerializerMethodField()
    certificate = serializers.SerializerMethodField()
    videos = VideoSerializer(many=True, read_only=True)  # ✅ use the correct related_name

    class Meta:
        model = Skill
        fields = [
            'id',
            'category',
            'profile_image',
            'full_name',
            'bio',
            'certificate',
            'experience',
            'skills',
            'created_at',
            'videos'   # ✅ correct name
        ]

    def get_profile_image(self, obj):
        request = self.context.get('request')
        if obj.profile_image and hasattr(obj.profile_image, 'url'):
            media_url = obj.profile_image.url.replace('/media/', '/api/media/')
            return request.build_absolute_uri(media_url)
        return None

    def get_certificate(self, obj):
        request = self.context.get('request')
        if obj.certificate and hasattr(obj.certificate, 'url'):
            media_url = obj.certificate.url.replace('/media/', '/api/media/')
            return request.build_absolute_uri(media_url)
        return None
    
class UpdateSkillSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(write_only=True, required=False)
    video_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Skill
        fields = [
            'id',
            'category_name',
            'profile_image',
            'full_name',
            'bio',
            'certificate',
            'experience',
            'skills',
            'video_file',
        ]
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # Optional: update category if given
        category_name = validated_data.pop('category_name', None)
        if category_name:
            try:
                category = Category.objects.get(
                    user=user,
                    category_name=category_name
                )
            except Category.DoesNotExist:
                raise serializers.ValidationError({
                    "category_name": "Invalid category for this user. Please create it first."
                })
            instance.category = category

        # Optional: add new video if given
        video_file = validated_data.pop('video_file', None)
        if video_file:
    # Remove the old video if it exists
            old_video = instance.videos.first()
            if old_video:
                old_video.video_file.delete(save=False)
                old_video.video_file = video_file
                old_video.save()
            else:
                Video.objects.create(
                    skill=instance,
                    user=user,
                    video_file=video_file
                )


        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


    