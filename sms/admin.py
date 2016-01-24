from django.contrib import admin

# Register your models here.
from .models import Smser

class SmserAdmin(admin.ModelAdmin):
	list_display = ['number', 'from_city', 'from_state', 'timestamp', 'updated']

admin.site.register(Smser, SmserAdmin)