from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('add_lead/', views.add_lead, name='add_lead'),
    path('export_csv/', views.export_customers_csv, name='export_customers_csv'),
    path('predict/', views.predict_conversion_probability, name='predict'),
    path('send_reminder/<int:customer_id>/', views.send_reminder, name='send_reminder'),
    path('send_reminder/<int:lead_id>/', views.send_reminder, name='send_reminder'),
    path('edit_customer/<int:pk>/', views.edit_customer, name='edit_customer'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/events/', views.calendar_events, name='calendar_events'),
    path('upload/customers/', views.upload_customers_csv, name='upload_customers'),
    path('upload/leads/', views.upload_leads_csv, name='upload_leads'),
    path('export/customers/', views.export_customers_csv, name='export_customers_csv'),


]
