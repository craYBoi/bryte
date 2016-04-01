from django.contrib import admin

# Register your models here.
from .models import TimeSlot, Book, NextShoot, Signup

admin.site.register(TimeSlot)
admin.site.register(Book)
admin.site.register(NextShoot)
admin.site.register(Signup)