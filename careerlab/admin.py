from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# Register your models here.
from .models import Timeslot, Booking, Signup, Nextshoot

class NextshootAdmin(ImportExportModelAdmin):
	pass

admin.site.register(Timeslot)
admin.site.register(Booking)
admin.site.register(Signup)
admin.site.register(Nextshoot, NextshootAdmin)
