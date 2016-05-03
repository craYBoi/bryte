from django.contrib import admin

# Register your models here.
from .models import Timeslot, Booking, Signup, Nextshoot


admin.site.register(Timeslot)
admin.site.register(Booking)
admin.site.register(Signup)
admin.site.register(Nextshoot)