from django.contrib import admin
from .models import Userdata, Upload, Share

# Register your models here.
admin.site.register(Userdata)
admin.site.register(Upload)
admin.site.register(Share)