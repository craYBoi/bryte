from django.contrib import admin

# Register your models here.
from .models import Photographer, PhotographerImage, Rating

class PhotographerAdmin(admin.ModelAdmin):
	list_display = ['first_name', 'last_name', 'short_description']

admin.site.register(Photographer, PhotographerAdmin)
admin.site.register(PhotographerImage)
admin.site.register(Rating)