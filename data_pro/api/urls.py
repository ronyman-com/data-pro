
# data_pro/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'visas', views.VisaViewSet)
router.register(r'passports', views.PassportViewSet)
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'transports', views.TransportServiceViewSet)



urlpatterns = [
    path('', include(router.urls)),
    # Only include this once in your project:
    path('auth/', include('rest_framework.urls', namespace='drf_auth'))
]