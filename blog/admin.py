from django.contrib import admin

# Register your models here.
from .models import Blog

class BlogAdmin(admin.ModelAdmin):
	list_display = ['title']


admin.site.register(Blog, BlogAdmin)