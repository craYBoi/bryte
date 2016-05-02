from django.contrib import admin

# Register your models here.
from .models import Timeslot, Booking, Signup


admin.site.register(Timeslot)
admin.site.register(Booking)
admin.site.register(Signup)