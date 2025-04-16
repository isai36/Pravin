from django.db import models
from django.contrib.auth.models import User
from sharedoc.utils.crypto import CryptoUtils
from django.core.files.base import ContentFile
import mimetypes

# Create your models here.
class Userdata(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    displayed_name = models.CharField(max_length=64, null=True)
    phone = models.CharField(max_length=255)

    def __str__(self, *args, **kwargs):
        self.displayed_name = CryptoUtils.hash(self.username)
        self.phone = CryptoUtils.encrypt(self.phone)
        super(Userdata, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username if self.user else "Unknown User"

class Upload(models.Model):
    filename = models.CharField(max_length=20)
    filepath = models.FileField(upload_to='')
    filetype = models.CharField(max_length=50, blank=True)
    shared_by = models.ForeignKey(Userdata, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_pdf(self):
        return self.filename.endswith(".pdf")

class Share(models.Model):
    sharedfile = models.ForeignKey(Upload, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(Userdata, on_delete=models.CASCADE, null=True, blank=True, related_name="received_shares")
    shared_with_raw = models.CharField(max_length=255, null=True, blank=True)
    shared_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(max_length=255)

    def save(self, *args, **kwargs):
        if self.notes:
            self.notes = CryptoUtils.encrypt(self.notes)
        super(Share, self).save(*args, **kwargs)