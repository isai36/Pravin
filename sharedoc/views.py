import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Userdata, Upload, Share
from .forms import LoginForm, RegisterForm, FileUploadForm

# Create your views here.
def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']

            user = authenticate(request, username=phone, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid phone number or password')
    else:
        form = LoginForm()

    return render(request, 'home.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['phone'], 
                password=form.cleaned_data['password']
            )
            user.save()

            userdata = Userdata(
                username=form.cleaned_data['username'],
                phone=form.cleaned_data['phone']
            )
            userdata.save()

            login(request, user)
            messages.success(request, 'Account created successfully')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

@login_required
def dashboard(request):
    #check if user is authenticated
    userdata = request.user.username

    context = {}
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            if(Userdata.objects.filter(phone=form.cleaned_data['sentto']).exists() == False):
                messages.error(request, 'User does not exist')
                return redirect('dashboard')

            file = request.FILES['file']
            uploaded_file = handle_uploaded_file(file)
            messages.success(request, 'File is uploaded successfully')

            upload = Upload(
                filename=file.name,
                filepath=uploaded_file,
                shared_by=Userdata.objects.get(phone=userdata)
            )
            upload.save()

            share = Share(
                shared_with=form.cleaned_data['sentto'],
                sharedfile=upload,
                notes=form.cleaned_data['notes']
            )
            share.save()
            messages.success(request, 'File is shared successfully')
    else:
        form = FileUploadForm()
    context['form'] = form
    
    try:
        context['share'] = Share.objects.filter(shared_with=userdata)
    except Share.DoesNotExist:
        context['share'] = None

    try:
        context['uploads'] = Upload.objects.filter(shared_by=Userdata.objects.get(phone=userdata))
    except Upload.DoesNotExist:
        context['uploads'] = None

    context['username'] = userdata
    return render(request, 'dashboard.html', context)

def handle_uploaded_file(f):
    file_path = os.path.join(settings.MEDIA_ROOT, f.name)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    return f'{f.name}'

def download_shared_file(request, share_id):
    if request.user.is_authenticated:
        userdata = request.user.username

        shared_file = get_object_or_404(Share, id=share_id)
        if shared_file.shared_with == str(userdata):
            file = shared_file.sharedfile

            response = HttpResponse(file.filepath.open('rb'), content_type='applcation/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file.filename}"'
            return response
        else:
            raise Http404("File not found.")
    else:
        raise Http404("You are not authorized to download this file.")
