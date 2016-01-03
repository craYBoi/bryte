from django import forms

from .models import Reservation

class ReserveForm(forms.ModelForm):
	class Meta:
		model = Reservation
		fields = ['first_name', 'last_name', 'photographer', 'email', 'phone', 'note']
 	# def clean_email(self):
