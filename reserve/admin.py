from django.contrib import admin

# Register your models here.
from .models import Reservation

class ReservationAdmin(admin.ModelAdmin):
	list_display = ['first_name', 'email', 'note']

admin.site.register(Reservation, ReservationAdmin)