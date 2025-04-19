import os

from django.views import View
from sharedoc.utils.crypto import CryptoUtils
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
from django.db import transaction
from django.urls import reverse, NoReverseMatch
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from two_factor.plugins.phonenumber.models import PhoneDevice
from two_factor.utils import default_device
from twilio.rest import Client
from sharedoc.utils.validators import format_malaysian_phone
from django.contrib.auth import login as auth_login

# Create your views here.
@csrf_protect
def custom_login_view(request):
    form = LoginForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        phone = format_malaysian_phone(form.cleaned_data['phone'])
        password = form.cleaned_data['password']

        try:
            userdata = Userdata.objects.get(phone=phone)
            user = authenticate(request, username=userdata.user.username, password=password)
        except Userdata.DoesNotExist:
            user = None

        if user:
            request.session['otp_user_id'] = user.id

            device = default_device(user)
            if not device:
                device = PhoneDevice.objects.create(user=user, name='default', number=phone, confirmed=True)

            otp = device.generate_challenge()
            print("Generated OTP:", otp)
            send_sms_otp(device.number, otp)

            return redirect('verify_otp')
        else:
            messages.error(request, 'Invalid phone or password.')

    return render(request, 'home.html', {'form': form})
    
def send_sms_otp(phone_number, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    print("User phone number:", phone_number)

    try:
        formatted_number = format_malaysian_phone(str(phone_number))
        print("Formatted phone number:", formatted_number)
        message = client.messages.create(
            body="Hello, Your OTP for sharedoc is: " + str(otp),
            from_='+19786506458',
            to=formatted_number
        )
        print("Message SID:", message.sid)
        return message.sid
    except Exception as e:
        print("Error sending SMS:", e)
        return None

@csrf_protect
def verify_otp(request):
    if request.method == 'POST':
        user_id = request.session.get('otp_user_id')
        token = request.POST.get('otp')

        if not user_id:
            messages.error(request, 'Session expired. Please log in again.')
            return redirect('login')

        try:
            user = User.objects.get(id=user_id)
            device = default_device(user)

            if device and device.verify_token(token):
                auth_login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid OTP.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')

    return render(request, 'verify_otp.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            displayed_name = form.cleaned_data['username']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if User.objects.filter(username=phone).exists():
                messages.error(request, 'This email is already taken. Please choose a different one.')
            elif password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            else:
                try:
                    phone = format_malaysian_phone(phone)
                    with transaction.atomic():
                        user = User.objects.create_user(
                            username=phone, 
                            password=password,
                        )
                        user.is_active = True
                        user.save()

                        userdata = Userdata(
                            user=user,
                            displayed_name=displayed_name,
                            phone=phone
                        )
                        userdata.save()

                        PhoneDevice.objects.create(user=user, name='default', number=phone, confirmed=True)
                    
                    messages.success(request, 'Account created successfully.')
                    
                    login(request, user)
                    return redirect('/account/login/')
                except Exception as e:
                    messages.error(request, f'An error occurred. Please try again later.  {e}')
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
            try:
                recipient = Userdata.objects.get(phone=form.cleaned_data['sentto'])
            except Userdata.DoesNotExist:
                messages.error(request, 'User does not exist')
                return redirect('dashboard')

            file = request.FILES['file']
            uploaded_file = handle_uploaded_file(file)
            messages.success(request, 'File is uploaded successfully')

            upload = Upload(
                filename=file.name,
                filepath=uploaded_file,
                shared_by=Userdata.objects.get(user=request.user)
            )
            upload.save()

            share = Share(
                shared_with=recipient,
                sharedfile=upload,
                notes=form.cleaned_data['notes']
            )
            share.save()
            messages.success(request, 'File is shared successfully')
    else:
        form = FileUploadForm()
    context['form'] = form
    
    try:
        context['share'] = Share.objects.filter(shared_with=Userdata.objects.get(user=request.user))
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

    # Save file first
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # Read and encrypt file content
    with open(file_path, 'rb') as original_file:
        encrypted = CryptoUtils.encrypt(original_file.read())

    # Overwrite with encrypted content
    with open(file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)
    
    return f.name

def download_shared_file(request, share_id):
    if request.user.is_authenticated:
        userdata = request.user.username

        shared_file = get_object_or_404(Share, id=share_id)
        if str(shared_file.shared_with) == str(userdata):
            file_obj = shared_file.sharedfile.filepath
            print("File path:", file_obj.path)

            if not file_obj.storage.exists(file_obj.name):
                raise Http404("Encrypted file not found on disk (Heroku wiped it).")

            with file_obj.open('rb') as f:
                encrypted_content = f.read()

            decrypted_content = CryptoUtils.decrypt(encrypted_content)
            response = HttpResponse(decrypted_content, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{shared_file.sharedfile.filename}"'
            return response
        else:
            raise Http404("Unauthorized to download this file.")
    else:
        raise Http404("You are not authenticated.")
    
def test_reverse(request):
    try:
        url = reverse('two_factor:login')
        return HttpResponse(f"Login URL: {url}")
    except NoReverseMatch:
        return HttpResponse("two_factor:login not found!")
