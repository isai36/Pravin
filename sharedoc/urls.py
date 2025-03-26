from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('download/<int:share_id>/', views.download_shared_file, name="download_file"),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
]