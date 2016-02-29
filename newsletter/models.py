from __future__ import unicode_literals

from photographer.models import Photographer
from django.db import models

# Create your models here.
class SignUp(models.Model):
	email = models.EmailField()
	full_name = models.CharField(max_length=120,blank=True, null=True)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)

	def __unicode__(self):
		return self.email


class Price(models.Model):
	title = models.CharField(max_length=120)
	shared_title = models.CharField(max_length=120, blank=True, null=True)
	subtitle = models.CharField(max_length=150, blank=True, null=True)
	price = models.PositiveSmallIntegerField(blank=True, null=True)
	stripe_price = models.IntegerField(blank=True, null=True)
	is_photography = models.BooleanField(default=False)
	is_videography = models.BooleanField(default=False)
	photographer = models.ManyToManyField(Photographer, blank=True)

	PACKAGE_CATEGORIES = (
		('re', 'Real Estate'),
		('sb', 'Small Business'),
	)
	category = models.CharField(max_length=20, choices=PACKAGE_CATEGORIES, default='re')


	def __unicode__(self):
		return self.title + ' ' + self.shared_title

	def save(self, *args, **kwargs):
		self.stripe_price = 100 * self.price
		super(Price, self).save(*args, **kwargs)

	class Meta:
		ordering = ['pk']

class PriceFeature(models.Model):
	price = models.ForeignKey(Price)
	feature_text = models.CharField(max_length=200)

	def __unicode__(self):
		return self.price.title + ' ' + str(self.price.price)
