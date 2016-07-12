from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

# Register your models here.
from .models import Timeslot, Booking, Signup, Nextshoot, HeadshotImage, ImagePurchase

class NextshootAdmin(ImportExportModelAdmin):
	list_display = ['id', 'photographer', 'location', 'school', 'active', 'name' ,'timestamp']

class BookingAdmin(ImportExportModelAdmin):
	list_display = ['id', 'email', 'name', 'timeslot', 'hash_id', 'dropbox_folder', 'upgrade_folder_path', 'show_up', 'timestamp', 'school_year', 'headshot_for', 'professional_path']

class TimeslotAdmin(admin.ModelAdmin):
	list_display = ['id', 'time', 'shoot','current_volumn', 'is_available']

class SignupAdmin(admin.ModelAdmin):
	list_display = ['id', 'email', 'name','notified', 'shoot', 'timestamp', 'school_year', 'headshot_for', 'professional_path']

class HeadshotImageAdmin(ImportExportModelAdmin):
	list_display = ['id', 'book', 'name', 'is_raw', 'is_fav','is_top','is_portrait', 'o_url', 'wt_url', 'wo_url']

class ImagePurchaseAdmin(ImportExportModelAdmin):
	list_display = ['id', 'image', 'email','option', 'value', 'charge_successful','is_delivered', 'is_copied', 'timestamp']


admin.site.register(Timeslot, TimeslotAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Signup, SignupAdmin)
admin.site.register(Nextshoot, NextshootAdmin)
admin.site.register(HeadshotImage, HeadshotImageAdmin)
admin.site.register(ImagePurchase, ImagePurchaseAdmin)
