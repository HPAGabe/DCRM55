from django.contrib import admin
from website.models import CustomerRecord

class RecordAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'city', 'state', 'zipcode', 'year', 'make', 'model', 'vin_last_8', 'date_sold')

admin.site.register(CustomerRecord, RecordAdmin)
