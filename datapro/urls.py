from django.contrib import admin
from django.urls import path, include
from data_pro.admin.home import *
from django.views.generic import RedirectView
from data_pro.admin.views import DashboardView
from data_pro.admin.views import *
from data_pro.views import *

urlpatterns = [
    path('system-admin/', admin.site.urls),
    path('', SystemLandingView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('superadmin/', SuperAdminPanelView.as_view(), name='SuperAdminPanelView'),
    path('system/settings/', SystemSettingsView.as_view(), name='system-settings'),
    
    # Redirect /system/ to /system/dashboard/
    #path('system/', RedirectView.as_view(url='dashboard/', permanent=True)),
    
    # Include your app URLs with namespace
    path('system/', include(('data_pro.urls'), namespace='system')),
    
    path('api/', include('data_pro.api.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    
]
