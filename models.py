from django.db import models
from django.core.exceptions import ValidationError
from .config import MAX_WEEKLY_PAYMENTS, MAX_BIWEEKLY_PAYMENTS, MAX_MONTHLY_PAYMENTS

class CustomerRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Customer Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=20)
    
    # Vehicle Information
    year = models.IntegerField(null=True, blank=True)
    make = models.CharField(max_length=50, null=True, blank=True)
    model = models.CharField(max_length=50, null=True, blank=True)
    vin_last_8 = models.CharField(max_length=8, null=True, blank=True)
    date_sold = models.DateField(null=True, blank=True)
    
    # Payment Information
    total_down_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    customer_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field
    payment_frequency = models.CharField(max_length=20, choices=[('Weekly', 'Weekly'), ('Bi-Weekly', 'Bi-Weekly'), ('Monthly', 'Monthly')], null=True, blank=True)
    payment_start_date = models.DateField(null=True, blank=True)
    next_payment_due = models.DateField(null=True, blank=True)
    num_payments = models.IntegerField(null=True, blank=True)
    
    def clean(self):
        # Validation logic for the number of payments
        if self.payment_frequency and self.num_payments:
            if self.payment_frequency == 'Weekly' and self.num_payments > MAX_WEEKLY_PAYMENTS:
                raise ValidationError(f'Maximum number of weekly payments is {MAX_WEEKLY_PAYMENTS}.')
            if self.payment_frequency == 'Bi-Weekly' and self.num_payments > MAX_BIWEEKLY_PAYMENTS:
                raise ValidationError(f'Maximum number of bi-weekly payments is {MAX_BIWEEKLY_PAYMENTS}.')
            if self.payment_frequency == 'Monthly' and self.num_payments > MAX_MONTHLY_PAYMENTS:
                raise ValidationError(f'Maximum number of monthly payments is {MAX_MONTHLY_PAYMENTS}.')

class PaymentSchedule(models.Model):
    customer = models.ForeignKey(CustomerRecord, on_delete=models.CASCADE, related_name='schedules')
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payments_made = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=(('Active', 'Active'), ('Completed', 'Completed'), ('Adjusted', 'Adjusted')))
    
    def __str__(self):
        return f"{self.customer.first_name} {self.customer.last_name}"
