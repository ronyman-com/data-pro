from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from data_pro.system.home import *
from django.views.generic import RedirectView
from data_pro.system.views import *
from django.conf.urls.static import static
from data_pro.system.views import *
from data_pro.views.superuser import *

superuser_patterns = [
    path('', SuperAdminDashboardView.as_view(), name='dashboard'),
   
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/update/', ClientUpdateView.as_view(), name='client-update'),
    #path('logs/', SystemLogsView.as_view(), name='system-logs'),
    path('settings/', SystemSettingsView.as_view(), name='system-settings'),
]

urlpatterns = [
    path('system-admin/', admin.site.urls),
    path('', SystemLandingView.as_view(), name='home'),
    path('dashboard/', SystemDashboardView.as_view(), name='dashboard'),
    path('superadmin/', SuperAdminPanelView.as_view(), name='SuperAdminPanelView'),
    path('system/settings/', SystemSettingsView.as_view(), name='system-settings'),
    
    # Redirect /system/ to /system/dashboard/
    path('system/', RedirectView.as_view(url='dashboard/', permanent=True)),
    
    # Include your app URLs with namespace
    path('system/', include(('data_pro.urls'), namespace='system')),
    
    path('api/', include('data_pro.api.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
