from django.contrib import admin

# Register your models here.
from .forms import SignUpForm
from .models import SignUp, Price, PriceFeature, ContactSale, ContactHelp

class SignUpAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', 'timestamp', 'updated']
	form = SignUpForm

class PriceAdmin(admin.ModelAdmin):
	list_display = ['pk', 'price', 'title', 'shared_title', 'is_photography']

class PriceFeatureAdmin(admin.ModelAdmin):
	list_display = ['pk', 'price', 'feature_text']

class ContactSaleAdmin(admin.ModelAdmin):
	list_display = ['pk', 'name', 'email', 'organization', 'category', 'amount', 'question']

class ContactHelpAdmin(admin.ModelAdmin):
	list_display = ['pk', 'name', 'email', 'question']


admin.site.register(SignUp, SignUpAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(PriceFeature, PriceFeatureAdmin)
admin.site.register(ContactSale, ContactSaleAdmin)
admin.site.register(ContactHelp, ContactHelpAdmin)