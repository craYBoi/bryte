from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from import_export import fields

# Register your models here.
from .models import Timeslot, Booking, Signup, Nextshoot, OriginalHeadshot, HeadshotPurchase, HeadshotOrder


class HpResource(resources.ModelResource):

	# image = fields.Field(column_name='Image/Email')
	# special_request = fields.Field(column_name='Special Request')
	# background = fields.Field(column_name='Background')
	photoshoot = fields.Field(column_name='photoshoot folder')

	class Meta:
		model = HeadshotPurchase

		fields = ('image', 'touchup', 'background', 'special_request',)
		
	def dehydrate_image(self, headshotpurchase):
		return headshotpurchase.image.__unicode__()

	def dehydrate_touchup(self, headshotpurchase):
		return headshotpurchase.get_touchup_display()

	def dehydrate_background(self, headshotpurchase):
		return headshotpurchase.get_background_display()

	def dehydrate_photoshoot(self, headshotpurchase):
		return headshotpurchase.image.booking.timeslot.shoot


class BookingResource(resources.ModelResource):

	class Meta:
		model = Booking
		fields = ('id', 'name', 'email', 'timeslot')

	def dehydrate_timeslot(self, booking):
		return booking.timeslot.time.strftime('%m/%d %H:%M')


class NextshootAdmin(ImportExportModelAdmin):
	list_display = ['id', 'photographer', 'location', 'school', 'active', 'name' , 'max_volumn' , 'is_serving', 'timestamp']
	

class TimeslotAdmin(admin.ModelAdmin):
	list_display = ['id', 'time', 'shoot','current_volumn', 'is_available']

class SignupAdmin(admin.ModelAdmin):
	list_display = ['id', 'email', 'name','notified', 'shoot', 'timestamp', 'cancelled']

class OriginalHeadshotAdmin(admin.ModelAdmin):
	list_display = ['id','booking', 'name', 'raw_url', 'deliverable_url', 'hash_id']

class HeadshotOrderAdmin(admin.ModelAdmin):
	list_display = ['id', 'booking', 'total', 'timestamp', 'address', 'copied_to_touchup', 'copied_to_prod', 'delivered', 'touchup_folder']

class HeadshotPurchaseAdmin(ImportExportModelAdmin):

	resource_class = HpResource

	list_display = ['pk', 'image', 'order', 'touchup', 'background', 'package', 'total', 'special_request', 'charged', 'copied', 'copied_to_touchup', 'copied_to_prod', 'delivered']



class BookingAdmin(ImportExportModelAdmin):
	resource_class = BookingResource

	list_display = ['id', 'email', 'name', 'timeslot', 'hash_id', 'dropbox_folder', 'upgrade_folder_path', 'show_up', 'cust_type', 'timestamp']

admin.site.register(OriginalHeadshot, OriginalHeadshotAdmin)
admin.site.register(HeadshotOrder, HeadshotOrderAdmin)
admin.site.register(HeadshotPurchase, HeadshotPurchaseAdmin)
# class HeadshotImageAdmin(ImportExportModelAdmin):
# 	list_display = ['id', 'book', 'name', 'is_raw', 'is_fav','is_top','is_portrait', 'o_url', 'wt_url', 'wo_url']

# class ImagePurchaseAdmin(ImportExportModelAdmin):
# 	list_display = ['id', 'image', 'email','option', 'value', 'charge_successful','is_delivered', 'is_copied', 'timestamp']


admin.site.register(Timeslot, TimeslotAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Signup, SignupAdmin)
admin.site.register(Nextshoot, NextshootAdmin)
# admin.site.register(HeadshotImage, HeadshotImageAdmin)
# admin.site.register(ImagePurchase, ImagePurchaseAdmin)
