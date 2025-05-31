from django.urls import path
from django.contrib.auth.decorators import login_required
from data_pro.views.superuser import *
from data_pro.views.clients import *
from data_pro.views.customers import *
from data_pro.views.invoices import *
from data_pro.views.passports import *
from data_pro.views.transports import *
from data_pro.views.vehicles import *
from data_pro.views.visas import *
from data_pro.system.views import *





app_name = 'data_pro'

urlpatterns = [
    # Authentication
    
    # Dashboard
    path('dashboard/', SystemDashboardView.as_view(), name='dashboard'),
    # urls.py
    path('client/quick-create/', ClientQuickCreateView.as_view(), name='client-quick-create'),
    
    # Customer Management
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/create/', CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer-edit'),
    path('customers/import/', CustomerImportView.as_view(), name='customer-import'),
    path('customers/export/', CustomerExportView.as_view(), name='customer-export'),
    path('customers/<int:pk>/status/', CustomerStatusView.as_view(), name='customer-status'),
    path('customers/<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer-delete'),

    # Vehicle Management
    path('vehicles/', VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/create/', VehicleCreateView.as_view(), name='vehicle-create'),
    path('vehicles/<int:pk>/', VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicles/<int:pk>/update/', VehicleUpdateView.as_view(), name='vehicle-update'),
    path('vehicles/<int:pk>/status/', VehicleStatusView.as_view(), name='vehicle-status'),
    path('vehicles/<int:pk>/delete/', VehicleDeleteView.as_view(), name='vehicle-delete'),

    # Visa Management
    path('visas/', VisaListView.as_view(), name='visa-list'),
    path('visas/create/', VisaCreateView.as_view(), name='visa-create'),
    path('visas/<int:pk>/update/', VisaUpdateView.as_view(), name='visa-update'),
    path('visas/<int:pk>/status/', VisaStatusView.as_view(), name='visa-status'),
    path('visas/<int:pk>/delete/', VisaDeleteView.as_view(), name='visa-delete'),

    # Transport Management
    path('transports/', TransportListView.as_view(), name='transport-list'),
    path('transports/create/', TransportCreateView.as_view(), name='transport-create'),
    path('transports/<int:pk>/', TransportDetailView.as_view(), name='transport-detail'),
    path('transports/<int:pk>/update/', TransportUpdateView.as_view(), name='transport-update'),
    path('transports/<int:pk>/status/', TransportStatusView.as_view(), name='transport-status'),
    path('transports/<int:pk>/delete/', TransportDeleteView.as_view(), name='transport-delete'),

    # Invoice Management
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoices/create/', InvoiceCreateView.as_view(), name='invoice-create'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoices/<int:pk>/update/', InvoiceUpdateView.as_view(), name='invoice-update'),
    path('invoices/<int:pk>/status/', InvoiceStatusView.as_view(), name='invoice-status'),
    path('invoices/<int:pk>/delete/', InvoiceDeleteView.as_view(), name='invoice-delete'),
    
    # Client Management
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client-edit'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client-delete'),

    # Passport Management
    path('passports/', PassportListView.as_view(), name='passport-list'),




    # ... existing passport URLs ...
    path('passport-extensions/', PassportExtensionListView.as_view(), name='passport-extension-list'),
    path('passport-extensions/create/', PassportExtensionCreateView.as_view(), name='passport-extension-create'),
    path('passport-extensions/<int:pk>/', PassportExtensionDetailView.as_view(), name='passport-extension-detail'),
    path('passport-extensions/<int:pk>/update/', PassportExtensionUpdateView.as_view(), name='passport-extension-update'),
    path('passport-extensions/<int:pk>/complete/', PassportExtensionCompleteView.as_view(), name='passport-extension-complete'),
    path('customers/<int:customer_id>/passports/create/', PassportCreateView.as_view(), name='passport-create'),
    path('passports/<int:pk>/update/', PassportUpdateView.as_view(), name='passport-update'),
    path('passports/<int:pk>/delete/', PassportDeleteView.as_view(), name='passport-delete'),
    path('passports/<int:pk>/status/', PassportStatusView.as_view(), name='passport-status'),
    

]