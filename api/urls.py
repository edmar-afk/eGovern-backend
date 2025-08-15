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
    
    
    path('file/<int:folder_id>/upload/<int:user_id>/', views.FileUploadView.as_view(), name='file-upload'),
    path('folders/<int:folder_id>/files/', views.FolderFilesListView.as_view(), name='folder-files-list'),
    path('files/', views.AllFilesView.as_view(), name='all-files'),
    path('files/<int:pk>/delete/', views.FolderFileDeleteView.as_view(), name='delete_folder_file'),
    path('files/<int:pk>/archive/', views.FileArchiveView.as_view(), name='archive_folder_file'),
    path('files/archives/', views.FileArchiveListView.as_view(), name='folder_file_archives'),
    path('files/<int:pk>/unarchive/', views.FileUnarchiveView.as_view(), name='folder_file_unarchive'),
]
