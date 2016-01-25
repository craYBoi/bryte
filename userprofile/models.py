from __future__ import unicode_literals

from django.db import models
from registration.signals import user_registered
# Create your models here.
from django.contrib.auth.models import User
import stripe


class Profile(models.Model):
	user = models.OneToOneField(User)
	name = models.CharField(max_length=120)
	stripe_id = models.CharField(max_length=200, null=True, blank=True)

	def __unicode__(self):
		return self.user.username

	def create_stripe_id(self):
		if not self.stripe_id:
			stripe_dict = stripe.Customer.create(email=self.user.email)
			self.stripe_id = stripe_dict.get('id')


def profileCallback(sender, request, user, **kwargs):
	userProfile, is_created = Profile.objects.get_or_create(user=user)
	if is_created:
		userProfile.name = user.username
		stripe_dict = stripe.Customer.create(email=user.email)
		userProfile.stripe_id = stripe_dict.get('id')
		userProfile.save()
	# for safety
	else: 
		if not userProfile.name:
			userProfile.name = user.username
		if not userProfile.stripe_id:
			stripe_dict = stripe.Customer.create(email=user.email)
			userProfile.stripe_id = stripe_dict.get('id')
		userProfile.save()


user_registered.connect(profileCallback)