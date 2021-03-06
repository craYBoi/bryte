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
	photoshoot_id = fields.Field(column_name='Photoshoot id')
	image_id = fields.Field(column_name='Image id')
	name = fields.Field(column_name='Name')
	school = fields.Field(column_name='School')
	shoot_date = fields.Field(column_name='Photoshoot Date')


	class Meta:
		model = HeadshotPurchase

		fields = ('image_id', 'name', 'school', 'shoot_date', 'photoshoot_id', 'touchup', 'background', 'special_request')
		
		export_order = ('name', 'school', 'shoot_date', 'image_id', 'photoshoot_id', 'touchup', 'background', 'special_request')

	def dehydrate_image_id(self, headshotpurchase):
		return headshotpurchase.image.pk

	def dehydrate_name(self, headshotpurchase):
		return headshotpurchase.order.booking.name

	def dehydrate_school(self, headshotpurchase):
		return headshotpurchase.order.booking.timeslot.shoot.school

	def dehydrate_shoot_date(self, headshotpurchase):
		return headshotpurchase.order.booking.timeslot.shoot.date

	def dehydrate_touchup(self, headshotpurchase):
		return headshotpurchase.get_touchup_display()

	def dehydrate_background(self, headshotpurchase):
		return headshotpurchase.get_background_display()

	def dehydrate_photoshoot_id(self, headshotpurchase):
		return headshotpurchase.image.booking.timeslot.shoot.pk


class HoResource(resources.ModelResource):
	name = fields.Field(column_name='Full Name')
	school = fields.Field(column_name='School')
	date = fields.Field(column_name='Shoot Date')

	class Meta:
		model = HeadshotOrder

		fields = ('booking', 'name', 'date', 'school', 'total', 'timestamp', 'address',)
		
	def dehydrate_booking(self, headshotorder):
		return headshotorder.booking.__unicode__()

	def dehydrate_school(self, headshotorder):
		return headshotorder.booking.timeslot.shoot.school

	def dehydrate_date(self, headshotorder):
		return headshotorder.booking.timeslot.shoot.date

	def dehydrate_name(self, headshotorder):
		return headshotorder.booking.name

	def dehydrate_total(self, headshotorder):
		return '$' + str(headshotorder.total)

	def dehydrate_timestamp(self, headshotorder):
		return headshotorder.timestamp.strftime('%Y/%m/%d %H:%M')

	def dehydrate_address(self, headshotorder):
		return headshotorder.address


class BookingResource(resources.ModelResource):

	class Meta:
		model = Booking
		fields = ('id', 'name', 'email', 'timeslot', 'shoot')

	def dehydrate_timeslot(self, booking):
		return booking.timeslot.time.strftime('%m/%d %H:%M')

	def dehydrate_id(self, booking):
		return booking.timeslot.shoot.location


class NextshootAdmin(ImportExportModelAdmin):
	list_display = ['id', 'photographer', 'location', 'school', 'active', 'name' , 'max_volumn' , 'is_serving', 'area', 'noshow_signup', 'timestamp']
	

class TimeslotAdmin(admin.ModelAdmin):
	list_display = ['id', 'time', 'shoot','current_volumn', 'is_available']

class SignupAdmin(admin.ModelAdmin):
	list_display = ['id', 'email', 'name','notified', 'shoot', 'timestamp', 'cancelled', 'is_sub']

class OriginalHeadshotAdmin(admin.ModelAdmin):
	list_display = ['id','booking', 'name', 'raw_url', 'deliverable_url', 'hash_id']

class HeadshotOrderAdmin(ImportExportModelAdmin):

	resource_class = HoResource

	list_display = ['id', 'name', 'school', 'shoot_date', 'book_id', 'total', 'timestamp', 'address', 'copied_to_touchup', 'copied_to_prod', 'delivered', 'touchup_folder', 'express_shipping', 'feedback_rating']

	def name(self, obj):
		return obj.booking.name

	def school(self, obj):
		return obj.booking.timeslot.shoot.school

	def shoot_date(self, obj):
		return obj.booking.timeslot.shoot.date

	def book_id(self, obj):
		return obj.booking.pk



class HeadshotPurchaseAdmin(ImportExportModelAdmin):

	resource_class = HpResource

	list_display = ['pk', 'photo_id', 'name', 'school', 'shoot_date','photoshoot_id', 'headshot_order_id', 'touchup', 'background', 'package', 'total', 'special_request', 'get_order_address', 'charged', 'copied', 'copied_to_touchup', 'copied_to_prod', 'delivered']

	def name(self, obj):
		return obj.order.booking.name

	def photoshoot_id(self, obj):
		return obj.order.booking.timeslot.shoot.pk

	def school(self, obj):
		return obj.order.booking.timeslot.shoot.school

	def shoot_date(self, obj):
		return obj.order.booking.timeslot.shoot.date

	def photo_id(self, obj):
		return obj.image.pk

	def headshot_order_id(self, obj):
		return obj.order.pk




class BookingAdmin(ImportExportModelAdmin):
	resource_class = BookingResource

	list_display = ['id', 'email', 'name', 'timeslot', 'hash_id', 'dropbox_folder', 'upgrade_folder_path', 'show_up', 'cust_type', 'discount_amount', 'is_sub', 'checked_in', 'is_taken_photo', 'timestamp']

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
