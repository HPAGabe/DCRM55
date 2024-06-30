from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import CustomerRecord, PaymentSchedule
from .config import MAX_WEEKLY_PAYMENTS, MAX_BIWEEKLY_PAYMENTS, MAX_MONTHLY_PAYMENTS

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = PaymentSchedule
        fields = ['start_date', 'end_date', 'total_amount']

class AdjustScheduleForm(forms.ModelForm):
    class Meta:
        model = PaymentSchedule
        fields = ['end_date', 'total_amount']
        
class AddRecordForm(forms.ModelForm):
    # Customer Information
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"First Name", "class":"form-control"}), label="")
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Last Name", "class":"form-control"}), label="")
    email = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Email", "class":"form-control"}), label="")
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Phone", "class":"form-control"}), label="")
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Address", "class":"form-control"}), label="")
    city = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"City", "class":"form-control"}), label="")
    state = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"State", "class":"form-control"}), label="")
    zipcode = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Zipcode", "class":"form-control"}), label="")

    # Vehicle Information
    year = forms.IntegerField(required=False, widget=forms.widgets.NumberInput(attrs={"placeholder":"Year", "class":"form-control"}), label="")
    make = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Make", "class":"form-control"}), label="")
    model = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Model", "class":"form-control"}), label="")
    vin_last_8 = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Last 8 of VIN", "class":"form-control"}), label="")
    date_sold = forms.DateField(required=False, widget=forms.widgets.DateInput(attrs={"placeholder":"Date Sold", "class":"form-control", "type":"date"}), label="")

    # Payment Information
    total_down_payment = forms.DecimalField(required=False, widget=forms.widgets.NumberInput(attrs={"placeholder":"Total Down Payment", "class":"form-control"}), label="")
    customer_paid = forms.DecimalField(required=False, widget=forms.widgets.NumberInput(attrs={"placeholder":"Customer Paid", "class":"form-control"}), label="")
    discount_amount = forms.DecimalField(required=False, widget=forms.widgets.NumberInput(attrs={"placeholder":"Discount Amount", "class":"form-control"}), label="")
    payment_frequency = forms.ChoiceField(required=False, choices=[('Weekly', 'Weekly'), ('Bi-Weekly', 'Bi-Weekly'), ('Monthly', 'Monthly')], widget=forms.Select(attrs={"class":"form-control"}), label="")
    payment_start_date = forms.DateField(required=False, widget=forms.widgets.DateInput(attrs={"placeholder":"Payment Start Date", "class":"form-control", "type":"date"}), label="")
    next_payment_due = forms.DateField(required=False, widget=forms.widgets.DateInput(attrs={"placeholder":"Next Payment Due", "class":"form-control", "type":"date"}), label="", disabled=True)

    class Meta:
        model = CustomerRecord
        exclude = ("user",)

    def clean(self):
        cleaned_data = super().clean()
        num_payments = cleaned_data.get('num_payments')
        payment_frequency = cleaned_data.get('payment_frequency')
        
        if num_payments is not None and payment_frequency is not None:
            if payment_frequency == 'Weekly' and num_payments > MAX_WEEKLY_PAYMENTS:
                raise forms.ValidationError(f'Maximum number of weekly payments is {MAX_WEEKLY_PAYMENTS}.')
            if payment_frequency == 'Bi-Weekly' and num_payments > MAX_BIWEEKLY_PAYMENTS:
                raise forms.ValidationError(f'Maximum number of bi-weekly payments is {MAX_BIWEEKLY_PAYMENTS}.')
            if payment_frequency == 'Monthly' and num_payments > MAX_MONTHLY_PAYMENTS:
                raise forms.ValidationError(f'Maximum number of monthly payments is {MAX_MONTHLY_PAYMENTS}.')

        return num_payments
