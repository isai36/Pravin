from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Phone number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Password'}))

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Username'}))
    phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Phone number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-4', 'placeholder': 'Confirm Password'}))
    accept_privacy_policy = forms.BooleanField(label="I agree to the privacy policy", required=True,
                                               widget=forms.CheckboxInput(attrs={'class': 'form-check-input mb-3'}))

class FileUploadForm(forms.Form):
    sentto = forms.CharField(label="Send to", max_length=11, widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': '0123456789'}))
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file mb-2'}))
    notes = forms.CharField(label=False , max_length=255, widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'placeholder': 'Notes'}))