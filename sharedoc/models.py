from django.db import models
import mimetypes

# Create your models here.
class Userdata(models.Model):
    username = models.CharField(max_length=20)
    phone = models.CharField(max_length=11)

class Upload(models.Model):
    filename = models.CharField(max_length=20)
    filepath = models.FileField(upload_to='')
    filetype = models.CharField(max_length=50, blank=True)
    shared_by = models.ForeignKey(Userdata, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        mime_type = mimetypes.guess_type(self.filename)[0]

        if mime_type:
            self.filetype = mime_type.split('/')[0]
        else:
            self.filetype = 'unknown'
        super(Upload, self).save(*args, **kwargs)

    @property
    def is_pdf(self):
        return self.filename.endswith(".pdf")

class Share(models.Model):
    sharedfile = models.ForeignKey(Upload, on_delete=models.CASCADE)
    shared_with = models.CharField(max_length=11, null=True)
    shared_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(max_length=255)