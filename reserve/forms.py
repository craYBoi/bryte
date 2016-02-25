from django import forms
from django.core.mail import send_mail

from .models import Reservation
from photographer.models import Photographer
from newsletter.models import Price



class ReserveForm(forms.Form):
	business_name = forms.CharField()
	email = forms.EmailField()
	phone = forms.RegexField(regex=r'^\+?1?\d{9,15}$')
	phone.error_messages['invalid'] = ("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	date_range = forms.CharField(label='Date Range (please give us a range of approximate dates)')
	special_request = forms.CharField(widget = forms.Textarea, required=False)

 	# def clean_email(self):
	# def send_txt(self):

	def send_email(self):
		send_mail('Successfully Registered!',
			'''
			Your Registration has been successfully made!
			''',
			'hello@brytephoto.com',
			['byyagp@gmail.com'],
			fail_silently=False)


class ReserveDetailStudentForm(forms.Form):
	ACCEPTABLE_FORMATS = [
		"%Y/%m/%d %H:%M"
	]
	package = forms.ModelChoiceField(queryset=Price.objects.all())
	datetime = forms.DateTimeField(input_formats=ACCEPTABLE_FORMATS, label='Start Time')
	phone = forms.RegexField(regex=r'^\+?1?\d{9,15}$')
	phone.error_messages['invalid'] = ("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	note = forms.CharField(widget = forms.Textarea, required=False)
	photographer = forms.ModelChoiceField(queryset=Photographer.objects.all(), widget = forms.HiddenInput())




