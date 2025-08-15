from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, ProfileSerializer, FolderSerializer, FileUnarchiveSerializer, FileArchiveSerializer, FolderFileCountSerializer, FolderTotalSizeSerializer, FolderFilesSerializer
from .models import Profile, Folders, Folder_Files
from django.shortcuts import get_object_or_404


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        print(serializer.errors)  # DEBUG: see why 400 happens
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            profile = Profile.objects.get(user__id=user_id)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateFolderView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FolderListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Folders.objects.all()
    serializer_class = FolderSerializer


class FolderFileCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, folder_id):
        folder = get_object_or_404(Folders, id=folder_id)
        file_count = Folder_Files.objects.filter(folder=folder).count()

        serializer = FolderFileCountSerializer({
            'folder_id': folder.id,
            'file_count': file_count
        })
        return Response(serializer.data, status=status.HTTP_200_OK)


class FolderDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, folder_id):
        folder = get_object_or_404(Folders, id=folder_id)
        serializer = FolderSerializer(folder)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FolderTotalSizeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, folder_id):
        folder = get_object_or_404(Folders, id=folder_id)
        serializer = FolderTotalSizeSerializer(folder)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteFolderView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, folder_id):
        folder = get_object_or_404(Folders, id=folder_id)
        folder.delete()
        return Response({"message": "Folder deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class FolderFilesListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = FolderFilesSerializer

    def get_queryset(self):
        folder_id = self.kwargs['folder_id']
        return Folder_Files.objects.filter(
            folder_id=folder_id,
            is_archive=False
        )
        
class FileArchiveListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = FolderFilesSerializer

    def get_queryset(self):
        return Folder_Files.objects.filter(is_archive=True)


class FileUploadView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, folder_id, user_id):
        try:
            folder = Folders.objects.get(id=folder_id)
        except Folders.DoesNotExist:
            return Response({"error": "Folder not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['folder'] = folder.id
        data['uploaded_by'] = user.id

        if 'file' in request.FILES:
            data['file_name'] = request.FILES['file'].name

        serializer = FolderFilesSerializer(data=data)  # ✅ use updated data
        if serializer.is_valid():
            serializer.save(folder=folder, uploaded_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllFilesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Folder_Files.objects.all()
    serializer_class = FolderFilesSerializer



class FolderFileDeleteView(generics.DestroyAPIView):
    queryset = Folder_Files.objects.all()
    serializer_class = FolderFilesSerializer
    permission_classes = [AllowAny]

    def perform_destroy(self, instance):
        if instance.file:
            instance.file.delete(save=False)  # remove from storage
        instance.delete()
        
class FileArchiveView(generics.UpdateAPIView):
    queryset = Folder_Files.objects.all()
    serializer_class = FileArchiveSerializer
    permission_classes = [AllowAny]
    
class FileUnarchiveView(generics.UpdateAPIView):
    queryset = Folder_Files.objects.all()
    serializer_class = FileUnarchiveSerializer
    permission_classes = [AllowAny]