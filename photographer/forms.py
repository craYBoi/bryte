from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
	user_email = forms.CharField(label='Email')
	class Meta:
		model = Rating
		fields = ['rating', 'comment']

 	# def clean_email(self):
