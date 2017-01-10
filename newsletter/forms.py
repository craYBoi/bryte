from django import forms

from .models import SignUp, PhotographerApplication

class SignUpForm(forms.ModelForm):
	class Meta:
		model = SignUp
		fields = ['email', 'full_name']

 	# def clean_email(self):


YEAR_IN_SCHOOL_CHOICE = [('Freshman', 'Freshman'), ('Sophomore', 'Sophomore'), ('Junior', 'Junior'), ('Senior', 'Senior'), ('Graduate Student', 'Graduate Student'), ('Other', 'Other')]

PHOTO_EXP_CHOICE = [('Less than 1 year', 'Less than 1 year'), ('1 to 2 years', '1 to 2 years'), ('More than 2 years', 'More than 2 years')]

class PhotographerApplicationForm(forms.Form):
	name = forms.CharField(label='Full name', max_length=120)
	email = forms.EmailField(label='Email')
	school = forms.CharField(max_length=60, label='School')
	year_in_school = forms.ChoiceField(
		widget=forms.Select,
		choices=YEAR_IN_SCHOOL_CHOICE,
		label='Your year in school',
	)
	dslr_model = forms.CharField(max_length=50, label='Your DSLR model and lens')
	prev_job = forms.CharField(max_length=200, label='Please describe your last paid job')
	photo_exp = forms.CharField(
		widget=forms.Select(choices=PHOTO_EXP_CHOICE),
		label='How many years of photography experience do you have?',
	)
	num_of_shoot = forms.CharField(max_length=100, label='How many photoshoots do you plan to do per semester? (Assuming each photoshoot lasts 5 hours)')
	flex_schedule = forms.CharField(max_length=100, label='Do you have a relatively flexible schedule?')
	portfolio_link = forms.CharField(max_length=100, required=False, label='Link to your portfolio')

