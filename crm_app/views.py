from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Customer, Lead
from .forms import CustomerForm, LeadForm
from datetime import datetime
from .utils.scraper import get_company_info
import csv
import joblib
import os
import matplotlib
matplotlib.use('Agg')  # For non-GUI matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.db.models import Count
import json
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages


# ---------------------------------------------
# 🔹 Home View - Show Dashboard, Customers, Leads, and Predictions
# ---------------------------------------------
from django.core.paginator import Paginator
from django.core.paginator import Paginator

from django.core.paginator import Paginator
from .models import Lead, Customer

from django.core.paginator import Paginator
from django.db.models import Q

def home(request):
    # Sorting for leads
    sort_by = request.GET.get('sort_by', 'follow_up_date')
    if sort_by not in ['follow_up_date', '-follow_up_date']:
        sort_by = 'follow_up_date'

    # Leads
    lead_queryset = Lead.objects.all().order_by(sort_by)
    lead_page = request.GET.get('lead_page', 1)
    lead_paginator = Paginator(lead_queryset, 10)  # Show 10 leads per page
    leads = lead_paginator.get_page(lead_page)

    # Customers
    search_query = request.GET.get('search', '')
    customer_queryset = Customer.objects.all()
    if search_query:
        customer_queryset = customer_queryset.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(company__icontains=search_query)
        )
    customer_page = request.GET.get('customer_page', 1)
    customer_paginator = Paginator(customer_queryset, 10)  # Show 10 customers per page
    customers = customer_paginator.get_page(customer_page)

    return render(request, 'crm_app/home.html', {
        'leads': leads,
        'customers': customers,
        'sort_by': sort_by,
        'query': search_query,
    })






# ---------------------------------------------
# 🔹 Add Customer View (includes web scraping company info)
# ---------------------------------------------
def add_customer(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        customer = form.save(commit=False)
        if not customer.company:
            customer.company = get_company_info(customer.name)
        customer.save()
        messages.success(request, "Customer added successfully!")
        return redirect('home')
    return render(request, 'crm_app/form.html', {
        'form': form,
        'title': 'Add Customer',
        'year': datetime.now().year
    })


# ---------------------------------------------
# 🔹 Add Lead View
# ---------------------------------------------
def add_lead(request):
    form = LeadForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'crm_app/form.html', {
        'form': form,
        'title': 'Add Lead',
        'year': datetime.now().year
    })


# ---------------------------------------------
# 🔹 Generate Bar Chart with Matplotlib
# ---------------------------------------------
def generate_lead_chart():
    statuses = Lead.objects.values_list('status', flat=True)
    status_list = list(statuses)
    status_count = {status: status_list.count(status) for status in set(status_list)}

    plt.figure(figsize=(6, 4))
    plt.bar(status_count.keys(), status_count.values(), color='teal')
    plt.title("Lead Status Overview")
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')


# ---------------------------------------------
# 🔹 Export Customers as CSV
# ---------------------------------------------
def export_customers_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=customers.csv'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Company', 'Created'])

    for c in Customer.objects.all():
        writer.writerow([c.name, c.email, c.phone, c.company, c.created_at])
    return response


# ---------------------------------------------
# 🔹 Predict Lead Conversion Probability (Manual)
# ---------------------------------------------
def predict_conversion_probability(request):
    if request.method == 'POST':
        feature1 = request.POST.get('feature1')
        feature2 = request.POST.get('feature2')

        # Basic validation
        if not feature1 or not feature2:
            return render(request, 'crm_app/lead_prediction.html', {
                'error': "Please enter both Follow-up Days and Has Company.",
            })

        try:
            feature1 = float(feature1)
            feature2 = float(feature2)
        except ValueError:
            return render(request, 'crm_app/lead_prediction.html', {
                'error': "Inputs must be numbers.",
            })

        import joblib, os
        model_path = os.path.join('crm_app', 'ml_model', 'model.pkl')
        model = joblib.load(model_path)

        prob = model.predict_proba([[feature1, feature2]])[0][1]
        return render(request, 'crm_app/lead_prediction.html', {
            'prob': round(prob * 100, 2)
        })

    return render(request, 'crm_app/lead_prediction.html')




# ---------------------------------------------
# 🔹 Predict Status of a Lead (Auto Prediction)
# ---------------------------------------------
import os
import joblib

def predict_lead_status(lead):
    # Set correct path to your model
    model_path = os.path.join(os.path.dirname(__file__), 'ml_model', 'model.pkl')
    model = joblib.load(model_path)

    follow_up_days = (lead.follow_up_date - lead.customer.created_at.date()).days if lead.follow_up_date else 0
    has_company = 1 if lead.customer.company else 0

    prediction = model.predict([[follow_up_days, has_company]])
    return 'Won' if prediction[0] == 1 else 'Lost'



# crm_app/views.py
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import get_object_or_404

def send_reminder(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    subject = f"⏰ Follow-up Reminder for {customer.name}"
    message = f"Dear {customer.name},\n\nThis is a reminder to follow up on your pending lead.\n\nBest regards,\nCRM Team"
    from_email = 'your_email@gmail.com'  # Replace with your Gmail or SMTP
    recipient_list = [customer.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        messages.success(request, f"Reminder sent to {customer.name}")
    except Exception as e:
        messages.error(request, f"Failed to send email: {e}")

    return redirect('home')

def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'crm_app/form.html', {'form': form, 'title': 'Edit Customer'})

from django.http import JsonResponse
# views.py
from django.shortcuts import render
from .models import Lead

def calendar_view(request):
    leads = Lead.objects.exclude(follow_up_date__isnull=True)
    events = []
    for lead in leads:
        events.append({
            'title': lead.title + " - " + lead.customer.name,
            'start': lead.follow_up_date.strftime('%Y-%m-%d')
        })
    return render(request, 'crm_app/calendar.html', {'events': events})

def calendar_events(request):
    leads = Lead.objects.select_related('customer').all()
    events = []
    for lead in leads:
        if lead.follow_up_date:
            events.append({
                "title": f"{lead.title} ({lead.customer.name})",
                "start": str(lead.follow_up_date)
            })
    return JsonResponse(events, safe=False)

import csv
from django.contrib import messages
from .models import Customer, Lead
from .forms import CSVUploadForm

def upload_customers_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['csv_file']
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                Customer.objects.get_or_create(
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    company=row['company']
                )
            messages.success(request, "Customers uploaded successfully!")
            return redirect('home')
    else:
        form = CSVUploadForm()
    return render(request, 'crm_app/upload_csv.html', {'form': form, 'title': 'Upload Customers CSV'})

def upload_leads_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['csv_file']
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                customer, _ = Customer.objects.get_or_create(name=row['customer'])
                Lead.objects.get_or_create(
                    title=row['title'],
                    customer=customer,
                    status=row['status'],
                    follow_up_date=row['follow_up_date']
                )
            messages.success(request, "Leads uploaded successfully!")
            return redirect('home')
    else:
        form = CSVUploadForm()
    return render(request, 'crm_app/upload_csv.html', {'form': form, 'title': 'Upload Leads CSV'})

import pandas as pd
from django.http import HttpResponse

def export_customers_csv(request):
    customers = Customer.objects.all().values()
    df = pd.DataFrame(customers)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=customers.csv'
    df.to_csv(path_or_buf=response, index=False)
    return response


# from django.shortcuts import render, redirect
# from .models import Customer, Lead
# from .forms import CustomerForm, LeadForm
# from .utils.scraper import get_company_info
# import matplotlib
# matplotlib.use('Agg')  # Use non-GUI backend before importing pyplot

# import matplotlib.pyplot as plt


# from datetime import datetime

# from .models import Customer, Lead
# from datetime import datetime
# from .utils import generate_lead_chart  # if you added chart
# from .ml import predict_lead_status     # add this after moving logic to ml.py

# def home(request):
#     customers = Customer.objects.all()
#     leads = Lead.objects.all()

#     # Add predictions to each lead object
#     for lead in leads:
#         lead.prediction = predict_lead_status(lead)

#     lead_chart = generate_lead_chart()  # if using matplotlib

#     return render(request, 'crm_app/home.html', {
#         'customers': customers,
#         'leads': leads,
#         'lead_chart': lead_chart,
#         'year': datetime.now().year
#     })


# def add_customer(request):
#     form = CustomerForm(request.POST or None)
#     if form.is_valid():
#         customer = form.save(commit=False)
#         if not customer.company:
#             customer.company = get_company_info(customer.name)
#         customer.save()
#         return redirect('home')
#     return render(request, 'crm_app/form.html', {'form': form, 'title': 'Add Customer','year': datetime.now().year
# })

# def add_lead(request):
#     form = LeadForm(request.POST or None)
#     if form.is_valid():
#         form.save()
#         return redirect('home')
#     return render(request, 'crm_app/form.html', {'form': form, 'title': 'Add Lead','year': datetime.now().year
# })

# import matplotlib.pyplot as plt
# from io import BytesIO
# import base64

# def generate_lead_chart():
#     from .models import Lead
#     statuses = Lead.objects.values_list('status', flat=True)
#     status_list = list(statuses)
#     status_count = {status: status_list.count(status) for status in set(status_list)}

#     import matplotlib.pyplot as plt
#     from io import BytesIO
#     import base64

#     plt.figure(figsize=(6,4))
#     plt.bar(status_count.keys(), status_count.values(), color='teal')
#     plt.title("Lead Status Overview")
#     plt.xlabel("Status")
#     plt.ylabel("Count")
    
#     buffer = BytesIO()
#     plt.tight_layout()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     image_png = buffer.getvalue()
#     buffer.close()
#     return base64.b64encode(image_png).decode('utf-8')


# # Update home view:
# def home(request):
#     from .models import Customer, Lead
#     customers = Customer.objects.all()
#     leads = Lead.objects.all()
#     chart = generate_lead_chart()
#     return render(request, 'crm_app/home.html', {'customers': customers, 'leads': leads, 'chart': chart,'year': datetime.now().year
# })

# import csv
# from django.http import HttpResponse

# def export_customers_csv(request):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename=customers.csv'
#     writer = csv.writer(response)
#     writer.writerow(['Name', 'Email', 'Phone', 'Company', 'Created'])

#     from .models import Customer
#     for c in Customer.objects.all():
#         writer.writerow([c.name, c.email, c.phone, c.company, c.created_at])
#     return response


# import joblib
# import numpy as np

# def predict_conversion_probability(request):
#     if request.method == 'POST':
#         feature1 = float(request.POST['feature1'])
#         feature2 = float(request.POST['feature2'])
#         model = joblib.load('crm_app/ml_model/model.pkl')
#         prob = model.predict_proba([[feature1, feature2]])[0][1]
#         return render(request, 'crm_app/lead_prediction.html', {'prob': round(prob * 100, 2),'year': datetime.now().year
# })
#     return render(request, 'crm_app/lead_prediction.html')


# import joblib
# import os

# def predict_lead_status(lead):
#     model_path = os.path.join(os.path.dirname(__file__), '..', 'crm_model.joblib')
#     model = joblib.load(model_path)

#     follow_up_days = (lead.follow_up_date - lead.customer.created_at.date()).days if lead.follow_up_date else 0
#     has_company = 1 if lead.customer.company else 0

#     prediction = model.predict([[follow_up_days, has_company]])
#     return 'Won' if prediction[0] == 1 else 'Lost'
