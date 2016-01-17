from django.contrib import admin

# Register your models here.
from .forms import SignUpForm
from .models import SignUp, Price, PriceFeature

class SignUpAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', 'timestamp', 'updated']
	form = SignUpForm

admin.site.register(SignUp, SignUpAdmin)
admin.site.register(Price)
admin.site.register(PriceFeature)