from __future__ import unicode_literals
from django.utils.text import slugify
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings


from uuid import uuid4
import dropbox
# -*- coding: utf-8 -*- 


class Photographer(models.Model):
	last_name = models.CharField(max_length=120)
	first_name = models.CharField(max_length=120, null=True, blank=True)
	email = models.EmailField(null=True, blank=True)
	slug = models.SlugField(unique=True, null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	phone = models.CharField(max_length=15, null=True, blank=True)
	profile = models.ImageField(upload_to='profile_img/', null=True, blank=True)
	total_rating = models.PositiveSmallIntegerField(null=True, blank=True)
	school = models.CharField(max_length=50, null=True, blank=True)
	location = models.CharField(max_length=50, null=True, blank=True)
	photography = models.BooleanField(blank=True, default=False)
	videography = models.BooleanField(blank=True, default=False)
	scope = models.CharField(max_length=20, null=True, blank=True)
	refresh_token = models.CharField(max_length=100, null=True, blank=True)
	access_token = models.CharField(max_length=100, null=True, blank=True)
	stripe_user_id = models.CharField(max_length=100, null=True, blank=True)
	stripe_publishable_key = models.CharField(max_length=100, null=True, blank=True)
	is_active = models.BooleanField(blank=True, default=False)
	is_featured = models.BooleanField(blank=True, default=False)
	dropbox_acct = models.CharField(max_length=120, null=True, blank=True)



	def __unicode__(self):
		return self.first_name + ' ' + self.last_name

	def get_full_name(self):
		return self.first_name + ' ' + self.last_name

	def save(self, *args, **kwargs):
		self.slug = slugify(self.first_name + ' ' + self.last_name)
		super(Photographer, self).save(*args, **kwargs)

	def get_absolute_url(self):
		full_name = self.first_name + ' ' + self.last_name
		full_name_slug = slugify(full_name)
		return reverse("photographer_detail", kwargs={"slug": self.slug})

	# create dropbox and share
	def share_dropbox(self, input_email):

		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		folder_path = '/' + str(self.get_full_name())


		shared_folder_id = None
		try:
			shared_folder = dbx.sharing_share_folder(folder_path)
			if shared_folder.is_complete():
				shared_folder_id = shared_folder.get_complete().shared_folder_id
		except dropbox.exceptions.ApiError:
			shared_folder_id = dbx.files_get_metadata(folder_path).shared_folder_id
			pass

		permission = 'editor'
		temp_member = dropbox.sharing.AddMember(
			member = dropbox.sharing.MemberSelector(
				'email',
				input_email
				),
			access_level = dropbox.sharing.AccessLevel(
				permission
				)
			)

		try:
			dbx.sharing_add_folder_member(
				shared_folder_id,
				[temp_member],
				quiet=True,
				custom_message='Hey ' + self.get_full_name() + '\nPlease upload the edited deliverables in here! Thanks!',
				)
		except dropbox.exceptions.ApiError:
			pass
		else:
			self.dropbox_acct = input_email
			self.save()


	def create_subfolder(self, folder_name):

		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		folder_path = '/' + str(self.get_full_name())

		new_folder_path = folder_path + '/' + str(folder_name)

		# if there's a folder with same name, pass
		try:
			dbx.files_create_folder(new_folder_path)
		except dropbox.exceptions.ApiError:
			pass
		else:
			return 1


	def create_share_link(self, folder_name):

		token = settings.DROPBOX_TOKEN
		dbx = dropbox.Dropbox(token)

		folder_path = '/' + str(self.get_full_name())

		new_folder_path = folder_path + '/' + str(folder_name)

		try:
			sharing_link = dbx.sharing_create_shared_link(new_folder_path, short_url=False, pending_upload=None)
		except dropbox.exceptions.ApiError:
			print 'sharing link error\n'
			pass
		else:
			return str(sharing_link.url)


	# for updating the review rating
	def calculate_total_rating(self):
		ratings = self.rating_set.all()
		rating_vals = [ra.rating for ra in ratings]
		average = sum(rating_vals)/float(len(rating_vals))
		self.total_rating = floor_to_int(average)


	def get_link_color_class(self):
			return 'dark_yellow'


	# some validation (email + phone) here

def image_upload_to(instance, filename):
	title = instance.author.last_name + '_' + instance.author.first_name
	slug = slugify(title)
	extension = filename.split('.')[-1]
	unique_name = filename.split('.')[0] + str(uuid4())
	return "photographer/%s/%s.%s" %(slug, unique_name, extension.lower())


class PhotographerImage(models.Model):
	author = models.ForeignKey(Photographer)
	image = models.ImageField(upload_to=image_upload_to)

	def __unicode__(self):
		return self.author.first_name


class PhotographerVideo(models.Model):
	author = models.ForeignKey(Photographer)
	video = models.CharField(max_length=120)
	title = models.CharField(max_length=50, blank=True, null=True)

	def __unicode__(self):
		return self.author.first_name


class Rating(models.Model):
	photographer = models.ForeignKey(Photographer)

	RATING_CHOICES = (
		(1, '1 Star'),
		(2, '2 Stars'),
		(3, '3 Stars'),
		(4, '4 Stars'),
		(5, '5 Stars'),
	)
	rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, null=True, blank=True)
	comment = models.TextField()
	email = models.EmailField()
	datetime = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.photographer.__unicode__()

	# override save to update total rating
	def save(self, *args, **kwargs):
		super(Rating, self).save(*args, **kwargs)

		# update the total rating of the photographer
		photographer = self.photographer
		photographer.calculate_total_rating()
		photographer.save()


class Package(models.Model):
	photographer = models.ForeignKey(Photographer)
	price = models.PositiveSmallIntegerField()
	title = models.CharField(max_length=50)
	level = models.CharField(max_length=50, blank=True, null=True)

	def __unicode__(self):
		return self.photographer.get_full_name() + ': ' + str(self.price)

	def save(self, *args, **kwargs):
		super(Package, self).save(*args, **kwargs)

		# update the price range of the photographer
		photographer = self.photographer
		photographer.calculate_price_range(self.price)
		photographer.save()

class PackageFeature(models.Model):
	package = models.ForeignKey(Package)
	feature_text = models.CharField(max_length=120)

	def __unicode__(self):
		return self.package.__unicode__()


from math import modf

def floor_to_int(input_floor):
	frac, whole = modf(input_floor)
	if frac < 0.5:
		return whole
	else:
		return whole + 1


class Specialty(models.Model):
	photographer = models.ForeignKey(Photographer)

	SPECIALTY_CHOICES = (
		('hs', 'Headshot'),
		('od', 'Outdoor'),
		('vt', 'Vintage'),
		('id', 'Indoor'),
		('pt', 'Portrait'),
	)
	specialty_text = models.CharField(max_length=120, choices=SPECIALTY_CHOICES)

	def __unicode__(self):
		return self.photographer.get_full_name()



