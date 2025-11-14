# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Folders, Folder_Files, Logs
from django.db import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']
        
class RegisterSerializer(serializers.ModelSerializer):
    address = serializers.CharField(
        write_only=True, required=False, allow_blank=True)
    profile_picture = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password',
            'first_name', 'last_name',
            'address', 'profile_picture'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        address = validated_data.pop('address', None)
        profile_picture = validated_data.pop('profile_picture', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        Profile.objects.create(
            user=user,
            address=address,
            profile_picture=profile_picture
        )

        return user


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'address', 'status', 'profile_picture']




class FolderSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Folders
        fields = ['id', 'name', 'created_by', 'date_creation']
        read_only_fields = ['created_by', 'date_creation']


class FolderFilesSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = Folder_Files
        fields = [f.name for f in Folder_Files._meta.fields] + \
            ['uploaded_by', 'file_size', 'is_confidential', 'is_archive']
        read_only_fields = ['uploaded_by', 'date_creation']

    def get_file_size(self, obj):
        if obj.file:
            size = obj.file.size  # bytes
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
        return "0 B"


class FolderFileCountSerializer(serializers.Serializer):
    folder_id = serializers.IntegerField()
    file_count = serializers.IntegerField()


class FolderTotalSizeSerializer(serializers.ModelSerializer):
    total_size_bytes = serializers.SerializerMethodField()
    total_size_human = serializers.SerializerMethodField()

    class Meta:
        model = Folders
        fields = ['id', 'name', 'created_by', 'date_creation',
                  'total_size_bytes', 'total_size_human']

    def get_total_size_bytes(self, obj):
        return sum(f.file.size for f in Folder_Files.objects.filter(folder=obj).exclude(is_archive=True) if f.file)

    def get_total_size_human(self, obj):
        size = self.get_total_size_bytes(obj)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 ** 3:
            return f"{size / (1024 ** 2):.2f} MB"
        else:
            return f"{size / (1024 ** 3):.2f} GB"


class FileArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder_Files
        fields = '__all__'
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        instance.is_archive = True
        instance.save()
        return instance


class FileUnarchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder_Files
        fields = '__all__'
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        instance.is_archive = False
        instance.save()
        return instance


class ConfidentialFileSerializer(serializers.ModelSerializer):
    file_size_bytes = serializers.SerializerMethodField()
    file_size_human = serializers.SerializerMethodField()

    class Meta:
        model = Folder_Files
        fields = [
            'id',
            'file_name',
            'file',
            'is_confidential',
            'is_archive',
            'date_creation',
            'file_size_bytes',
            'file_size_human',
        ]
        read_only_fields = ['is_confidential', 'date_creation',
                            'file_size_bytes', 'file_size_human']

    def get_file_size_bytes(self, obj):
        if obj.file:
            return obj.file.size
        return 0

    def get_file_size_human(self, obj):
        size = self.get_file_size_bytes(obj)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 ** 3:
            return f"{size / (1024 ** 2):.2f} MB"
        else:
            return f"{size / (1024 ** 3):.2f} GB"


class LogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = '__all__'


class FolderFilesTotalSizeSerializer(serializers.Serializer):
    total_size_bytes = serializers.SerializerMethodField()
    total_size_human = serializers.SerializerMethodField()

    def get_total_size_bytes(self, obj):
        total = 0
        for f in Folder_Files.objects.all():
            if f.file and hasattr(f.file, 'size'):
                try:
                    total += f.file.size
                except Exception:
                    pass  # skip files that can't be accessed
        return total

    def get_total_size_human(self, obj):
        size = self.get_total_size_bytes(obj)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
