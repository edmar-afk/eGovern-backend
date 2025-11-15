from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    status = models.TextField(default="Pending")
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"


class System_logs(models.Model):
    detail = models.TextField()
    detal_two = models.TextField(blank=True, null=True)
    log_date = models.DateTimeField(auto_now_add=True)


class Folders(models.Model):
    name = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)


class Folder_Files(models.Model):
    folder = models.ForeignKey(
        Folders, on_delete=models.CASCADE, blank=True, null=True)
    file_name = models.TextField(blank=True, null=True)
    file = models.FileField(
        upload_to='files/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg',
                                'png', 'docx', 'pdf', 'ppt', 'xls']
        )]
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    is_confidential = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    is_backup = models.BooleanField(default=False)



class Logs(models.Model):
    info1 = models.TextField(blank=True, null=True)
    info2 = models.TextField(blank=True, null=True)
    info3 = models.TextField(blank=True, null=True)
    info4 = models.TextField(blank=True, null=True)
    log_date = models.DateTimeField(auto_now_add=True)