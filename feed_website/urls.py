from django.contrib import admin
from django.urls import path, include
from formulation import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home page
    path('', views.index, name='index'),

    # Formulation app
    path('formulation/', include('formulation.urls')),

    # Authentication (login, logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
]


