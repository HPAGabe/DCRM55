from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from website.forms import SignUpForm, AddRecordForm, ScheduleForm, AdjustScheduleForm
from django.db.models import Q
import subprocess
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import os

from website.models import CustomerRecord, PaymentSchedule
from .config import MAX_WEEKLY_PAYMENTS, MAX_BIWEEKLY_PAYMENTS, MAX_MONTHLY_PAYMENTS

def home(request):
    query = request.GET.get('q')
    if query:
        records = CustomerRecord.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(address__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query) |
            Q(zipcode__icontains=query)
        )
    else:
        records = CustomerRecord.objects.all()
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
            return redirect('home')
        else:
            messages.success(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')
    else:
        return render(request, 'home.html', {'records': records})


def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('home')


def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You Have Successfully Registered! Welcome!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})

    return render(request, 'register.html', {'form': form})


def customer_record(request, pk):
    if request.user.is_authenticated:
        # Look Up Records
        customer_record = get_object_or_404(CustomerRecord, id=pk)
        return render(request, 'record.html', {'customer_record': customer_record})
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('home')


def delete_record(request, pk):
    if request.user.is_authenticated:
        delete_it = get_object_or_404(CustomerRecord, id=pk)
        delete_it.delete()
        messages.success(request, "Record Deleted Successfully...")
        return redirect('home')
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect('home')


def add_record(request):
    form = AddRecordForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                add_record = form.save()
                messages.success(request, "Record Added...")
                return redirect('home')
        return render(request, 'add_record.html', {'form': form})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')


def update_record(request, pk):
    if request.user.is_authenticated:
        current_record = get_object_or_404(CustomerRecord, id=pk)
        form = AddRecordForm(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.success(request, "Record Has Been Updated!")
            return redirect('home')
        return render(request, 'update_record.html', {'form': form, 'customer_record': current_record})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')


def generate_agreement_pdf_view(request, pk):
    customer = get_object_or_404(CustomerRecord, pk=pk)

    # Calculate payment details
    total_down_payment = customer.total_down_payment or 0
    discount_amount = customer.discount_amount or 0
    net_amount = total_down_payment - discount_amount
    payment_frequency = customer.payment_frequency
    if payment_frequency == 'Weekly':
        num_payments = min(52, MAX_WEEKLY_PAYMENTS)
    elif payment_frequency == 'Bi-Weekly':
        num_payments = min(26, MAX_BIWEEKLY_PAYMENTS)
    elif payment_frequency == 'Monthly':
        num_payments = min(12, MAX_MONTHLY_PAYMENTS)
    else:
        num_payments = 0
    payment_per_term = net_amount / num_payments if num_payments else 0

    # Render the HTML template with the customer data
    html_string = render_to_string('agreement.html', {
        'customer': customer,
        'net_amount': net_amount,
        'num_payments': num_payments,
        'payment_per_term': f'{payment_per_term:.2f}',
    })

    # Ensure the templates directory exists
    templates_dir = os.path.join(settings.BASE_DIR, 'website', 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)

    # Write the HTML string to a temporary file
    html_file_path = os.path.join(templates_dir, 'agreement_temp.html')
    with open(html_file_path, 'w') as html_file:
        html_file.write(html_string)

    # Ensure the output directory exists in the scripts directory
    output_dir = os.path.join(settings.BASE_DIR, 'scripts', 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the command to run the Node.js script
    command = ['node', os.path.join(settings.BASE_DIR, 'scripts', 'generate_pdf.js'), html_file_path, f'agreement_{pk}.pdf']

    # Run the command and capture output
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())  # Print standard output
        print(result.stderr.decode())  # Print error output
    except subprocess.CalledProcessError as e:
        return HttpResponse(f'Error generating PDF: {e.stderr.decode()}', status=500)

    # Return the generated PDF file as a response
    pdf_path = os.path.join(output_dir, f'agreement_{pk}.pdf')
    try:
        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename=agreement_{pk}.pdf'
            return response
    except FileNotFoundError:
        return HttpResponse('PDF file not found.', status=404)
    
def add_schedule(request, customer_id):
    customer = get_object_or_404(CustomerRecord, id=customer_id)
    form = ScheduleForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.customer = customer
            schedule.save()
            messages.success(request, "Schedule added successfully.")
            return redirect('customer_detail', customer_id=customer.id)  # Ensure this name and param are correct
        else:
            # If the form is not valid, re-render the form with validation errors
            return render(request, 'add_schedule.html', {'form': form, 'customer_id': customer_id})
    else:
        form = ScheduleForm()
    return render(request, 'add_schedule.html', {'form': form, 'customer_id': customer_id})

def adjust_schedule(request, schedule_id):
    schedule = get_object_or_404(PaymentSchedule, id=schedule_id)
    form = AdjustScheduleForm(request.POST or None, instance=schedule)
    if request.method == 'POST' and form.is_valid():
        form.save()
        schedule.status = 'Adjusted'
        schedule.save()
        messages.success(request, "Schedule adjusted successfully.")
        return redirect('customer_detail', customer_id=schedule.customer.id)
    return render(request, 'adjust_schedule.html', {'form': form, 'schedule': schedule})

def view_schedules(request, customer_id):
    customer = get_object_or_404(CustomerRecord, id=customer_id)
    schedules = customer.schedules.all()
    return render(request, 'view_schedules.html', {'customer': customer, 'schedules': schedules})

def customer_detail(request, customer_id):
    customer = get_object_or_404(CustomerRecord, pk=customer_id)
    print("Customer ID:", customer.id)  # Debug: Check the customer ID
    return render(request, 'record.html', {'customer': customer})

def some_view(request, customer_id):
    customer_record = get_object_or_404(CustomerRecord, pk=customer_id)
    return render(request, 'add_schedule.html', {'customer_record': customer_record})