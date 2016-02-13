from django import forms


class ProfileEditForm(forms.Form):
	first_name = forms.CharField()
	last_name = forms.CharField()
	email = forms.CharField(required=False)
	school = forms.CharField()
	phone = forms.RegexField(regex=r'^\+?1?\d{9,15}$')
	description = forms.CharField(widget = forms.Textarea, required=False)