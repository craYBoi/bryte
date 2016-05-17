from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# Register your models here.
from .models import Timeslot, Booking, Signup, Nextshoot

class NextshootAdmin(ImportExportModelAdmin):
	pass

class BookingAdmin(ImportExportModelAdmin):
	list_display = ['id', 'email', 'name', 'timeslot', 'hash_id', 'timestamp']
	pass

class TimeslotAdmin(admin.ModelAdmin):
	list_display = ['id', 'time', 'shoot','current_volumn']


class SignupAdmin(admin.ModelAdmin):
	list_display = ['id', 'email', 'name','notified', 'timestamp']


admin.site.register(Timeslot, TimeslotAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Signup, SignupAdmin)
admin.site.register(Nextshoot, NextshootAdmin)
