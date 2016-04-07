from __future__ import unicode_literals

from django.db import models
from photographer.models import Photographer
from django.utils import timezone

from datetime import datetime
# Create your models here.


class TimeSlot(models.Model):
	time = models.DateTimeField()
	is_available = models.BooleanField(default=True)

	def __unicode__(self):
		return self.time.strftime('%m/%d/%Y %I:%M %p')

	def time_slot_format(self):
		time_format =  self.time.strftime('%I:%M %p')
		if time_format[0] == '0':
			return time_format[1:]
		return time_format


class Book(models.Model):
	photographer = models.ForeignKey(Photographer)
	name = models.CharField(max_length=50)
	email = models.EmailField()
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	timeslot = models.ForeignKey(TimeSlot)

	def __unicode__(self):
		return self.name + ' ' + self.email + ' ' + str(self.timeslot)


class Signup(models.Model):
	email = models.EmailField()
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.email


class NextShoot(models.Model):
	date = models.DateField()
	photographer = models.ForeignKey(Photographer)
	location = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	class Meta:
		ordering = ('-timestamp',)

	def __unicode__(self):
		return str(self.date) + ' - ' + self.location + ' - ' + self.photographer.get_full_name()

	def time_format(self):
		return self.date.strftime('%B %d')