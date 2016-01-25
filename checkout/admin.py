from django.contrib import admin

# Register your models here.
from .models import Purchase

class PurchaseAdmin(admin.ModelAdmin):
	list_display = ['user', 'package', 'timestamp']

admin.site.register(Purchase, PurchaseAdmin)