from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from datetime import datetime
from photographer.models import Photographer

# Create your models here.

class Timeslot(models.Model):
	time = models.DateTimeField()
	is_available = models.BooleanField(default=True)
	current_volumn = models.PositiveSmallIntegerField(default=0)

	def __unicode__(self):
		return self.time.strftime('%m/%d/%Y %I:%M %p')

	def time_slot_format(self):
		time_format =  self.time.strftime('%I:%M %p')
		slot_left = ' ------ ' + str(5 - self.current_volumn) + '/5 slots left'
		time_format += slot_left
		if time_format[0] == '0':
			return time_format[1:]
		return time_format

	def increment(self):
		max_volumn = 5

		# this should not be happening
		if not self.is_available:
			print 'this should not be happening'

		if self.current_volumn < max_volumn and self.is_available:
			self.current_volumn += 1
			if self.current_volumn == max_volumn:
				self.is_available = False
			self.save()

	def reset(self):
		self.is_available = True
		self.current_volumn = 0



class Booking(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	timeslot = models.ForeignKey(Timeslot)

	def __unicode__(self):
		return self.name + ' ' + self.email + ' ' + str(self.timeslot)


class Signup(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.name + ' ' + self.email


class Nextshoot(models.Model):
	date = models.DateField()
	photographer = models.ForeignKey(Photographer, related_name='nextshoot_photographer')
	location = models.CharField(max_length=100)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	class Meta:
		ordering = ('-timestamp',)

	def __unicode__(self):
		return str(self.date) + ' - ' + self.location + ' - ' + self.photographer.get_full_name()

	def time_format(self):
		return self.date.strftime('%B %d')