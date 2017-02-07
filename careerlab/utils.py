from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from datetime import datetime
from datetime import timedelta
from random import SystemRandom
import string
import os
import dropbox
import StringIO
import csv

from .models import HeadshotPurchase, HeadshotOrder, Booking, Nextshoot


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
		writer.writerow(['Image name', 'Background', 'Resolution', 'Special Request'])

		
		for p in purchases:

			# customized add teeth whitening..
			if p.touchup == 4:
				sr = p.special_request
			else:
				sr = ''

			writer.writerow([str(p.id) + p.image.name, p.get_background_display(), p.get_touchup_display(), sr])

		# generate touchup list to send
		email = EmailMessage('Auto gened Touchup List Test', ' ', 'Bryte Photo <' + settings.EMAIL_HOST_USER + '>', ['byyagp@gmail.com'])
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
			count = 0
			for item in items:
				# assert item.name in image_names, 'No purchase instance found! ' + item.name

				file_name = item.name

				# parse the name to find id
				p_id = ''
				for c in file_name:
					if not c.isalpha():
						p_id += c
					else:
						break

				try:
					ind = p_ids.index(p_id)
				except ValueError, e:
					print 'already done that. ' + file_name
					continue

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

					count += 1

			print str(count) + ' files copied..'
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
			count = 0
			for item in items:
				# assert item.name in image_names, 'No purchase instance found! ' + item.name
				file_name = item.name

				# filter out temp files


				# parse the name to find id

				p_id = ''
				for c in file_name:
					if not c.isalpha():
						p_id += c
					else:
						break

				print p_id


				try:
					ind = p_ids.index(p_id)
				except ValueError, e:
					# for situations like manual copying
					print 'Already copied.. Continue ' + file_name 
					continue


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

					count += 1

			print str(count) + ' files copied..'
		else:
			print 'There aren\'t any photos in touchup deliverable yet'


def deliver_deliverable():
	shoots = Nextshoot.objects.all()
	for shoot in shoots:

		print 'working on ' + shoot.__unicode__()
		shoot.deliver_deliverables()

		print '\n'

	print 'DONE DELIVERING!'
		

def photo_to_touchup(folder_name):
	shoots = Nextshoot.objects.all()

	for shoot in shoots:
		print 'working on ' + shoot.__unicode__()
		shoot.photo_to_touchups(folder_name)

		print '\n'

	print 'DONE TRANSFERRING TO TOUCHUP'



# do everyday
def step_1(folder_name):
	create_touchup_folder(folder_name)
	generate_touchup_list(folder_name)
	photo_to_touchup(folder_name)



# list all the email actions
REMINDER = (-1, 'afternoon')
NOTIFICATION = (-1, 'evening')
MY_HEADSHOT = (2, '5-8 PM')
NO_FOLLOWUP_1 = (5, 'afternoon')
NO_FOLLOWUP_2 = (8, 'morning')
NO_FOLLOWUP_3 = (13, 'evening')
NO_FOLLOWUP_4 = (30, 'afternoon')
NO_FOLLOWUP_5 = (60, 'morning')

def email_time_list():
	shoots = Nextshoot.objects.all()
	time_list = []
	for shoot in shoots:
		date = shoot.date
		r = date + timedelta(days=REMINDER[0])
		n = date + timedelta(days=NOTIFICATION[0])
		m = date + timedelta(days=MY_HEADSHOT[0])
		nf1 = date + timedelta(days=NO_FOLLOWUP_1[0])
		nf2 = date + timedelta(days=NO_FOLLOWUP_2[0])
		nf3 = date + timedelta(days=NO_FOLLOWUP_3[0])
		nf4 = date + timedelta(days=NO_FOLLOWUP_4[0])
		nf5 = date + timedelta(days=NO_FOLLOWUP_5[0])

		time_list.append((shoot.school + ' - ' + shoot.date.strftime('%m-%d'), r, 'Reminder Email', REMINDER[1]))
		time_list.append((shoot.school + ' - ' + shoot.date.strftime('%m-%d'), n, 'Notification Email', NOTIFICATION[1]))
		time_list.append((shoot.school + ' - ' + shoot.date.strftime('%m-%d'), m, 'My Headshot Email', MY_HEADSHOT[1]))
		time_list.append((shoot.school + ' - ' + shoot.date.strftime('%m-%d'), nf1, 'No Followup 1', NO_FOLLOWUP_1[1]))
		time_list.append((shoot.school + ' - ' + shoot.date.strftime('%m-%d'), nf2, 'No Followup 2', NO_FOLLOWUP_2[1]))
		time_list.append((shoot.school + ' - ' + shoot.date.strftime('%m-%d'), nf3, 'No Followup 3', NO_FOLLOWUP_3[1]))
		time_list.append((shoot.school + ' - ' + shoot.date.strftime('%m-%d'), nf4, 'No Followup 4', NO_FOLLOWUP_4[1]))
		time_list.append((shoot.school + ' - ' + shoot.date.strftime('%m-%d'), nf5, 'No Followup 5', NO_FOLLOWUP_5[1]))

		#sorted_by_second = sorted(data, key=lambda tup: tup[1])
	sorted_time_list = sorted(time_list, key=lambda tup: tup[1])
	
	for t in sorted_time_list:
		if t[1] >= datetime.date(datetime.now()):
			print t[0] + ' -- ' + t[2] + ':  ' + t[1].strftime('%Y-%m-%d') + '\t' + t[3]





