from django import forms
from django.core.mail import send_mail
from .models import Reservation

class ReserveForm(forms.ModelForm):
	class Meta:
		model = Reservation
		fields = ['first_name', 'last_name', 'photographer', 'email', 'phone', 'note']
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