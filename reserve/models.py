from __future__ import unicode_literals

from django.db import models

from photographer.models import Photographer
from userprofile.models import Profile
from newsletter.models import Price


# Create your models here.
class Reservation(models.Model):
	photographer = models.ForeignKey(Photographer)
	profile = models.ForeignKey(Profile, blank=True, null=True)
	phone = models.CharField(max_length=15, blank=True)
	note = models.TextField(blank=True, null=True)
	datetime = models.DateTimeField()
	complete = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.profile.user.username