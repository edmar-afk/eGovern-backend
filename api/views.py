from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import ConfidentialFileSerializer, FolderFilesTotalSizeSerializer, RegisterSerializer, LogsSerializer, ProfileSerializer, FolderSerializer, FileUnarchiveSerializer, FileArchiveSerializer, FolderFileCountSerializer, FolderTotalSizeSerializer, FolderFilesSerializer
from .models import Profile, Folders, Folder_Files, Logs
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
import os
import tempfile
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from docx2pdf import convert
from urllib.parse import urlparse
from django.conf import settings
import traceback


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
        file_count = Folder_Files.objects.filter(
            folder=folder).exclude(is_archive=True).count()

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


class RenameFolderView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, folder_id):
        try:
            folder = Folders.objects.get(id=folder_id)
        except Folders.DoesNotExist:
            return Response({"error": "Folder not found"}, status=status.HTTP_404_NOT_FOUND)

        new_name = request.data.get("name")
        if not new_name:
            return Response({"error": "Name is required"}, status=status.HTTP_400_BAD_REQUEST)

        folder.name = new_name
        folder.save()

        serializer = FolderSerializer(folder)
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


class ConfidentialFileUploadView(generics.CreateAPIView):
    queryset = Folder_Files.objects.all()
    serializer_class = ConfidentialFileSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        user_id = self.kwargs.get("user_id")
        user = get_object_or_404(User, id=user_id)
        serializer.save(uploaded_by=user, is_confidential=True)


class ConfidentialFileListView(generics.ListAPIView):
    serializer_class = ConfidentialFileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Folder_Files.objects.filter(is_confidential=True)


class ConfidentialFileDeleteView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk, format=None):
        try:
            file = Folder_Files.objects.get(id=pk, is_confidential=True)
            file.file.delete(save=False)  # delete the actual file from storage
            file.delete()
            return Response({"detail": "Confidential file deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Folder_Files.DoesNotExist:
            return Response({"detail": "Confidential file not found."}, status=status.HTTP_404_NOT_FOUND)


class RecentUploadFileView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = FolderFilesSerializer

    def get_queryset(self):
        return Folder_Files.objects.filter(
            is_archive=False,
            is_confidential=False
        ).order_by('-date_creation')[:5]


class LogsCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = Logs.objects.all()
    serializer_class = LogsSerializer


class LogsListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Logs.objects.all().order_by('-log_date')
    serializer_class = LogsSerializer


class FolderFilesTotalSizeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = FolderFilesTotalSizeSerializer(instance={})
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def convert_to_pdf(request):
    file_url = request.data.get("fileUrl")
    if not file_url:
        return JsonResponse({"error": "fileUrl is required"}, status=400)

    try:
        parsed_url = urlparse(file_url)
        file_path = os.path.join(
            settings.MEDIA_ROOT, parsed_url.path.replace("/media/", ""))

        if not os.path.exists(file_path):
            return JsonResponse({"error": f"File not found at {file_path}"}, status=404)

        with tempfile.TemporaryDirectory() as tmpdirname:
            output_pdf = os.path.join(tmpdirname, "output.pdf")
            # ⚠️ this is where most errors happen
            convert(file_path, output_pdf)

            final_pdf_path = os.path.join(
                settings.MEDIA_ROOT,
                "converted",
                os.path.basename(file_path) + ".pdf"
            )
            os.makedirs(os.path.dirname(final_pdf_path), exist_ok=True)
            os.replace(output_pdf, final_pdf_path)

            pdf_url = request.build_absolute_uri(
                settings.MEDIA_URL + "converted/" +
                os.path.basename(file_path) + ".pdf"
            )
            return JsonResponse({"pdf_url": pdf_url})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)
