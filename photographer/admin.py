from django.contrib import admin

# Register your models here.
from .models import Photographer, PhotographerImage, Rating, Package, PackageFeature

class PhotographerAdmin(admin.ModelAdmin):
	list_display = ['first_name', 'last_name', 'short_description']

class RatingAdmin(admin.ModelAdmin):
	list_display = ['rating', 'comment']

class PackageAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', 'price', 'title']

class PackageFeatureAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', 'feature_text']

admin.site.register(Photographer, PhotographerAdmin)
admin.site.register(PhotographerImage)
admin.site.register(Package, PackageAdmin)
admin.site.register(PackageFeature, PackageFeatureAdmin)
admin.site.register(Rating, RatingAdmin)