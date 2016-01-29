from django.contrib import admin

# Register your models here.
from .models import Reservation

class ReservationAdmin(admin.ModelAdmin):
	list_display = ['photographer', 'price', 'note', 'phone', 'datetime']

admin.site.register(Reservation, ReservationAdmin)