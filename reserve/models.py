from __future__ import unicode_literals

from django.db import models
from photographer.models import Photographer

# Create your models here.
class Reservation(models.Model):
	photographer = models.ForeignKey(Photographer)
	first_name = models.CharField(max_length=120)
	last_name = models.CharField(max_length=120)
	email = models.EmailField()
	phone = models.CharField(max_length=120, blank=True, null=True)
	note = models.TextField(blank=True, null=True)

	def get_full_name(self):
		return self.first_name + ' ' + self.last_name

	def __unicode__(self):
		return self.get_full_name()
