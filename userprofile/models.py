from __future__ import unicode_literals

from django.db import models
from registration.signals import user_registered
# Create your models here.
from django.contrib.auth.models import User

from photographer.models import Photographer
import stripe


class Profile(models.Model):
	user = models.OneToOneField(User)
	name = models.CharField(max_length=120)
	photographer = models.OneToOneField(Photographer, related_name='userprofile', blank=True, null=True, on_delete=models.CASCADE)


	def __unicode__(self):
		return self.user.username

	def get_photographer_url(self):
		if self.photographer:
			return self.photographer.get_absolute_url()


def profileCallback(sender, request, user, **kwargs):
	userProfile, is_created = Profile.objects.get_or_create(user=user)

	if is_created:
		userProfile.name = user.username
		# stripe_dict = stripe.Customer.create(email=user.email)
		# userProfile.stripe_id = stripe_dict.get('id')
		# userProfile.save()
	# for safety
	else: 
		if not userProfile.name:
			userProfile.name = user.username
		# if not userProfile.stripe_id:
		# 	stripe_dict = stripe.Customer.create(email=user.email)
		# 	userProfile.stripe_id = stripe_dict.get('id')
		userProfile.save()

	# link photographer to the userprofile
	photographer, is_created = Photographer.objects.get_or_create(last_name=userProfile.name,
		first_name=userProfile.name)
	userProfile.photographer = photographer
	userProfile.save()

user_registered.connect(profileCallback)