from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login page becomes the home page
    path('', auth_views.LoginView.as_view(), name='home'),

    # Your app
    path('formulation/', include('formulation.urls')),

    # Login, Logout, Password Reset
    path('accounts/', include('django.contrib.auth.urls')),
]