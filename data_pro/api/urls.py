# data_pro/api/customer_urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.CustomerViewSet, basename='customers')

# Custom endpoints for customer-related actions
urlpatterns = [
    # CSV Import/Export (now handled as ViewSet actions)
    path('import_csv/', views.CustomerViewSet.as_view({'post': 'import_csv'}), name='customer-import-csv'),
    path('export_csv/', views.CustomerViewSet.as_view({'get': 'export_csv'}), name='customer-export-csv'),
    
    # Status management (now handled by BaseViewSet)
    path('<int:pk>/status/', views.CustomerViewSet.as_view({'post': 'status'}), name='customer-status'),
    
    # Additional customer endpoints can be added here
    path('<int:pk>/verify/', views.CustomerViewSet.as_view({'post': 'verify'}), name='customer-verify'),
] + router.urls