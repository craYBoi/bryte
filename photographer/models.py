from __future__ import unicode_literals
from django.utils.text import slugify
from django.db import models
from django.core.urlresolvers import reverse


class Photographer(models.Model):
	last_name = models.CharField(max_length=120)
	first_name = models.CharField(max_length=120)
	email = models.EmailField()
	slug = models.SlugField(unique=True, null=True, blank=True)
	short_description = models.CharField(max_length=150)
	description = models.TextField()
	phone = models.CharField(max_length=15)
	profile = models.ImageField(upload_to='profile/', null=True)
	total_rating = models.PositiveSmallIntegerField(null=True, blank=True)

	def __unicode__(self):
		return self.first_name + ' ' + self.last_name

	def save(self, *args, **kwargs):
		self.slug = slugify(self.first_name + ' ' + self.last_name)
		super(Photographer, self).save(*args, **kwargs)

	def get_absolute_url(self):
		full_name = self.first_name + ' ' + self.last_name
		full_name_slug = slugify(full_name)
		return reverse("photographer_detail", kwargs={"slug": self.slug})

	# for updating the review rating
	def calculate_total_rating(self):
		ratings = self.rating_set.all()
		rating_vals = [ra.rating for ra in ratings]
		average = sum(rating_vals)/float(len(rating_vals))
		self.total_rating = floor_to_int(average)


	# some validation (email + phone) here

def image_upload_to(instance, filename):
	title = instance.author.last_name + '_' + instance.author.first_name
	slug = slugify(title)
	extension = filename.split('.')[-1]
	return "photographer/%s/img.%s" %(slug, extension)


class PhotographerImage(models.Model):
	author = models.ForeignKey(Photographer)
	image = models.ImageField(upload_to=image_upload_to)

	def __unicode__(self):
		return self.author.first_name


class Rating(models.Model):
	photographer = models.ForeignKey(Photographer)
	rating = models.PositiveSmallIntegerField()
	comment = models.TextField()
	datetime = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.photographer.__unicode__()

	# override save to update total rating
	def save(self, *args, **kwargs):
		super(Rating, self).save(*args, **kwargs)
		photographer = self.photographer
		photographer.calculate_total_rating()
		photographer.save()


from math import modf

def floor_to_int(input_floor):
	frac, whole = modf(input_floor)
	if frac < 0.5:
		return whole
	else:
		return whole + 1



