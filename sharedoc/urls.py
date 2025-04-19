from django.contrib.auth import views as auth_views
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.custom_login_view, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('account/', include(('two_factor.urls', 'two_factor'), namespace='two_factor')),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('download/<int:share_id>/', views.download_shared_file, name="download_file"),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('test-reverse/', views.test_reverse, name="test_reverse"),
]