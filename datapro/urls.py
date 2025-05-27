"""
URL configuration for datapro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from data_pro.admin.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', include('data_pro.urls')),
    # path('passport/', include('datapro.passport.urls')),
]