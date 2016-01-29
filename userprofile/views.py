from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from .models import Profile
from reserve.models import Reservation


@login_required
def profile(request):
	user = request.user
	profile = user.profile
	reservations = Reservation.objects.filter(profile=profile).order_by('timestamp')
	context = {
		'name': user.username,
		'profile': profile,
		'reservations': reservations,
		'title_text': profile.user.username,
	}

	return render(request, 'profile.html', context)
