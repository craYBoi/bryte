from __future__ import unicode_literals

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
	price = models.PositiveSmallIntegerField()
	stripe_price = models.IntegerField()
	is_student = models.BooleanField()
	# create a choice for the type of photography
	# also create a choice for student, pro, or group (replacing is_student)

	def __unicode__(self):
		return self.title + ' ' + str(self.price)

	def save(self, *args, **kwargs):
		self.stripe_price = 100 * self.price
		super(Price, self).save(*args, **kwargs)

	def get_title(self):
		if self.is_student:
			return 'Student ' + self.title
		else:
			return 'Professional ' + self.title 


class PriceFeature(models.Model):
	price = models.ForeignKey(Price)
	feature_text = models.CharField(max_length=200)

	def __unicode__(self):
		return self.price.title + ' ' + str(self.price.price)
