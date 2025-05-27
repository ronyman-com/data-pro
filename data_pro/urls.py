"""
URL configuration for datapro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from admin.views import (
    CustomerListView,
    CustomerCreateView,
    CustomerUpdateView,
    CustomerImportView,
    CustomerExportView,
    # Import other views as needed
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Admin dashboard and customer management URLs
    path('dashboard/', login_required(CustomerListView.as_view()), name='admin-dashboard'),
    path('customers/', login_required(CustomerListView.as_view()), name='customer-list'),
    path('customers/create/', login_required(CustomerCreateView.as_view()), name='customer-create'),
    path('customers/<int:pk>/edit/', login_required(CustomerUpdateView.as_view()), name='customer-edit'),
    path('customers/import/', login_required(CustomerImportView.as_view()), name='customer-import'),
    path('customers/export/', login_required(CustomerExportView.as_view()), name='customer-export'),
    
    # Include other app URLs as needed
    # path('visa/', include('datapro.visa.urls')),
    # path('passport/', include('datapro.passport.urls')),
]