from django.conf import settings
from django.core.mail import send_mail, EmailMessage

from datetime import datetime
from random import SystemRandom
import string
import os
import dropbox
import StringIO
import csv

from .models import HeadshotPurchase, HeadshotOrder, Booking


# create daily touchup folder
def create_touchup_folder(folder_name):
	token = settings.DROPBOX_TOKEN
	dbx = dropbox.Dropbox(token)

	touchup_folder = settings.DROPBOX_TOUCHUP

	free_deliverable_path = os.path.join(touchup_folder, folder_name, 'Free', 'Deliverable')
	paid_deliverable_path = os.path.join(touchup_folder, folder_name, 'Upgraded', 'Deliverable')

	try:
		dbx.files_create_folder(free_deliverable_path)
		dbx.files_create_folder(paid_deliverable_path)
	except Exception, e:
		print '[FAIL] fail to create folder ' + folder_name
		raise e
	else:
		print '[SUCCESS] created folders ' + folder_name
		

# generate touchup list for mmp
def generate_touchup_list(folder_name):
	
	# orders = self.headshotorder_set.all()

	# right now do the linear scan on entire objects
	# in the future, do shoot class method or something more efficient

	# filter using the copied_to_touchup
	# make sure to do this BEFORE calling the photo_to_touchup
	purchases = HeadshotPurchase.objects.filter(copied_to_touchup=False).exclude(touchup=1)

	file_name = folder_name + '.csv'

	if purchases:

		print 'Generating ' + str(len(purchases)) + ' purchases for mmp...'
		# name should be folder name (date)

		csvf = StringIO.StringIO()
		writer = csv.writer(csvf)
		writer.writerow(['Image name', 'Background', 'Special Request'])

		for p in purchases:
			writer.writerow([str(p.id)+p.image.name, p.get_background_display(), p.special_request])

		# generate touchup list to send
		email = EmailMessage('Auto gened Touchup List Test', ' ', 'Bryte Photo <' + settings.EMAIL_HOST_USER + '>', [settings.EMAIL_HOST_USER])
		email.attach(file_name, csvf.getvalue(), 'text/csv')
		try:
			email.send()
		except Exception, e:
			print 'Touchup List not sent..'
			pass
		else:
			print 'Touchup List sent!'
		
		print 'Done..'

		# send the list to email

	else:
		print 'There\'s nothing to generate'



# touchup to prod, doesn't need to be the subclass of this
def touchup_to_prod_free(folder_name):
	token = settings.DROPBOX_TOKEN
	dbx = dropbox.Dropbox(token)

	orders = HeadshotOrder.objects.filter(touchup_folder=folder_name)

	# do the filtering in purchase for now
	purchases = []
	for o in orders:
		purchases.extend(o.headshotpurchase_set.filter(copied_to_prod=False))

	print 'purchases found!'
	p_ids = [str(p.id) for p in purchases]
	# print purchases

	touchup_folder_path = os.path.join(settings.DROPBOX_TOUCHUP, folder_name, 'Free', 'Deliverable')

	try:
		items = dbx.files_list_folder(touchup_folder_path).entries
	except Exception, e:
		raise e
	else:
		if items:
			for item in items:
				# assert item.name in image_names, 'No purchase instance found! ' + item.name

				file_name = item.name

				# parse the name to find id
				p_id = file_name[:file_name.index('IMG')]

				ind = p_ids.index(p_id)

				purchase_instance = purchases[ind]
				booking = purchase_instance.order.booking

				N = 6
				hash_code = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

				prod_path = os.path.join(booking.dropbox_folder, 'Deliverable', hash_code + item.name)

				# do the copy thing
				try:
					dbx.files_copy(item.path_lower, prod_path)
				except Exception, e:
					print '[FAIL] copy from touchup to prod ' + booking.email + ' ' + purchase_instance.image.name + ' Should not be happening'
				else:
					print '[SUCCESS] copy from touchup to prod ' + booking.email + ' ' + purchase_instance.image.name
					purchase_instance.copied_to_prod = True
					super(HeadshotPurchase, purchase_instance).save()

					# change the order flag as well
					# since all the purchases in one order will be moved to touchup and then to prod all together. If 1 purchase is copied to prod, that means its entire order has been copied to prod. TBTest

					purchase_instance.order.copied_to_prod = True
					super(HeadshotOrder, purchase_instance.order).save()
		else:
			print 'There aren\'t any photos in touchup deliverable yet'


def touchup_to_prod_paid(folder_name):
	token = settings.DROPBOX_TOKEN
	dbx = dropbox.Dropbox(token)

	orders = HeadshotOrder.objects.filter(touchup_folder=folder_name)

	# do the filtering in purchase for now
	purchases = []
	for o in orders:
		purchases.extend(o.headshotpurchase_set.filter(copied_to_prod=False))

	print 'purchases found!'
	p_ids = [str(p.id) for p in purchases]
	# print purchases

	touchup_folder_path = os.path.join(settings.DROPBOX_TOUCHUP, folder_name, 'Upgraded', 'Deliverable')

	try:
		items = dbx.files_list_folder(touchup_folder_path).entries
	except Exception, e:
		raise e
	else:
		if items:
			for item in items:
				# assert item.name in image_names, 'No purchase instance found! ' + item.name
				file_name = item.name

				# parse the name to find id
				p_id = file_name[:file_name.index('IMG')]

				ind = p_ids.index(p_id)

				purchase_instance = purchases[ind]
				booking = purchase_instance.order.booking

				N = 6
				hash_code = ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))


				prod_path = os.path.join(booking.dropbox_folder, 'Deliverable', hash_code + item.name)

				# do the copy thing
				try:
					dbx.files_copy(item.path_lower, prod_path)
				except Exception, e:
					print '[FAIL] copy from touchup to prod ' + booking.email + ' ' + purchase_instance.image.name + ' Should not be happening'
				else:
					print '[SUCCESS] copy from touchup to prod ' + booking.email + ' ' + purchase_instance.image.name
					purchase_instance.copied_to_prod = True
					super(HeadshotPurchase, purchase_instance).save()

					# change the order flag as well
					# since all the purchases in one order will be moved to touchup and then to prod all together. If 1 purchase is copied to prod, that means its entire order has been copied to prod. TBTest

					purchase_instance.order.copied_to_prod = True
					super(HeadshotOrder, purchase_instance.order).save()
		else:
			print 'There aren\'t any photos in touchup deliverable yet'