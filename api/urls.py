from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
# ssd
urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/<int:user_id>/', views.UserProfileView.as_view(), name='user-profile'),
    
    
    path('folders/create/<int:user_id>/', views.CreateFolderView.as_view(), name='create-folder'),
    path('folders/', views.FolderListView.as_view(), name='folder-list'),
    path('folders/<int:folder_id>/count/', views.FolderFileCountView.as_view(), name='folder-file-count'),
    path('folders/<int:folder_id>/total-size/', views.FolderTotalSizeView.as_view(), name='folder-total-size'),
    path('folders/<int:folder_id>/delete/', views.DeleteFolderView.as_view(), name='delete-folder'),
    path("folders/<int:folder_id>/rename/", views.RenameFolderView.as_view(), name="rename-folder"),
    
    path('file/<int:folder_id>/upload/<int:user_id>/', views.FileUploadView.as_view(), name='file-upload'),
    path('folders/<int:folder_id>/files/', views.FolderFilesListView.as_view(), name='folder-files-list'),
    path('files/', views.AllFilesView.as_view(), name='all-files'),
    path('files/<int:pk>/delete/', views.FolderFileDeleteView.as_view(), name='delete_folder_file'),
    path('files/<int:pk>/archive/', views.FileArchiveView.as_view(), name='archive_folder_file'),
    path('files/archives/', views.FileArchiveListView.as_view(), name='folder_file_archives'),
    path('files/<int:pk>/unarchive/', views.FileUnarchiveView.as_view(), name='folder_file_unarchive'),
    path('files/total-size/', views.FolderFilesTotalSizeView.as_view(), name='files-total-size'),

    path('file/upload/<int:user_id>/', views.ConfidentialFileUploadView.as_view(), name='confidential-file-upload'),
    path('file/confidential/', views.ConfidentialFileListView.as_view(), name='confidential-file-list'),
    path('confidential-files/<int:pk>/delete/', views.ConfidentialFileDeleteView.as_view(), name='confidential-file-delete'),
    path('files/recent-uploads/', views.RecentUploadFileView.as_view(), name='recent_upload_files'),
    
    
    path('upload-logs/', views.LogsCreateView.as_view(), name='upload-logs'),
    path('logs/', views.LogsListView.as_view(), name='logs-list'),
    
    
    path("convert-to-pdf/", views.convert_to_pdf, name="convert-to-pdf"),
    
    path('users/<int:user_id>/delete/', views.DeleteUserView.as_view()),
    path('non-staff-users/', views.NonStaffUsersView.as_view(), name='non-staff-users'),
    
    path('set-backup/<int:file_id>/', views.SetBackupAPIView.as_view(), name='set-backup'),
    path('files/backups/', views.FileBackupListView.as_view(), name='file_backups-list'),
    path('files/<int:pk>/unbackup/', views.FileUnbackupView.as_view(), name='unbackup_folder_file'),
]
