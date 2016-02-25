from __future__ import unicode_literals

from django.db import models

from photographer.models import Photographer
from userprofile.models import Profile
from newsletter.models import Price


# Create your models here.
class Reservation(models.Model):
	photographer = models.ForeignKey(Photographer)
	profile = models.ForeignKey(Profile, blank=True, null=True)
	first_name = models.CharField(max_length=100, blank=True, null=True)
	last_name = models.CharField(max_length=100, blank=True, null=True)
	price = models.ForeignKey(Price)
	phone = models.CharField(max_length=15)
	email = models.EmailField(blank=True, null=True)
	note = models.TextField(blank=True, null=True)
	date_range = models.CharField(max_length=150)
	business_name = models.CharField(max_length=100)
	datetime = models.DateTimeField(blank=True, null=True)
	complete = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.photographer.get_full_name()

