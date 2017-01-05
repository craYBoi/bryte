"""takeone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from newsletter import views as newsletter_views
from careerlab import views as careerlab_views
from sms import views as sms_views
from userprofile import views as profile_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', newsletter_views.home, name='home'),
    url(r'^about$', newsletter_views.about, name='about'),
    url(r'^photographer/', include('photographer.urls')),

    url(r'^partners/$', newsletter_views.clients, name='landing_clients'),
    url(r'^partners/[a-zA-Z]+/$', newsletter_views.clients, name='landing_clients_names'),
 
    url(r'^contact/', newsletter_views.contact, name='landing_contact'),
    url(r'^affordable/', newsletter_views.sales, name='landing_sales'),
    url(r'^family/', newsletter_views.family, name='landing_family'),

    url(r'^ajax_contact/', newsletter_views.ajax_contact, name='ajax_landing_contact'),
    url(r'^retrieve/', newsletter_views.retrieve, name='landing_retrieve'),
    # url(r'^myheadshots/', newsletter_views.test_retrieve, name='landing_retrieve1'),
    
    url(r'^ajax_retrieve/', newsletter_views.ajax_retrieve, name='ajax_landing_retrieve'),
    url(r'^help/', newsletter_views.help, name='landing_help'),
    url(r'^ajax_help/', newsletter_views.ajax_help, name='ajax_landing_help'),

    url(r'^test$', newsletter_views.test, name='test'),
    url(r'^test2$', newsletter_views.test2, name='test2'),
    url(r'^careercenter$', newsletter_views.signup_template, name='landing_signup_template'),

    

    # book
    url(r'^book/', include('book.urls')),

    # careerlab
    url(r'^school/', include('careerlab.urls')),

    # order 
    url(r'^headshot/$', careerlab_views.headshot_index, name='headshot_index'),
    url(r'^headshot/style$', careerlab_views.headshot_style, name='headshot_style'),
    url(r'^headshot/prints$', careerlab_views.headshot_print_frame, name='headshot_print_frame'),
    url(r'^headshot/review$', careerlab_views.headshot_review, name='headshot_review'),
    url(r'^headshot/checkout$', careerlab_views.headshot_checkout, name='headshot_checkout'),
    url(r'^headshot/complete$', careerlab_views.headshot_complete, name='headshot_complete'),
    url(r'^headshot/timeout$', careerlab_views.headshot_error, name='headshot_error'),
    url(r'^headshot/add$', careerlab_views.ajax_headshot_add, name='headshot_add'),
    url(r'^headshot/remove$', careerlab_views.ajax_headshot_remove, name='headshot_remove'),
    url(r'^headshot/expire$', careerlab_views.headshot_expire, name='headshot_expire'),
    url(r'^headshot/addkeepsake$', careerlab_views.ajax_keepsake_add, name='headshot_keepsake_add'),
    url(r'^headshot/payment$', careerlab_views.headshot_payment, name='headshot_payment'),
    # url(r'^Careerlab/', include('careerlab.urls')),
    # url(r'^careerlab/', include('careerlab.urls')),
    # url(r'^RIC/', include('careerlab.urls')),
    # url(r'^ric/', include('careerlab.urls')),

    # reserve
    url(r'^reserve/', include('reserve.urls')),

    # packages
    url(r'^packages$', newsletter_views.package, name='packages'),

    # faqs
    url(r'^faq$', newsletter_views.faq, name='faqs'),

    # become a photographer
    url(r'^photographers$', newsletter_views.photographer_app, name='photographer_app'),
    url(r'^photographers/apply$', newsletter_views.become_photographer, name='become_photographer'),
    url(r'^photographers/apply/start$', newsletter_views.photographer_app_form, name='photographer_app_form'),
    url(r'^photographers/manual$', newsletter_views.photographer_manual, name='photographer_manual'),
    # select photographer
    url(r'^select$', newsletter_views.select_photographer, name='select_photographer'),

    # blogs 
    url(r'^blog/', include('blog.urls')),

    # user profile
    url(r'^profile$', profile_views.profile, name='profile'),
    # edit profile
    url(r'^profile/edit', profile_views.edit, name='profile_edit'),


    # registration 
    url(r'^accounts/', include('registration.backends.simple.urls')),

    # legal stuff
    url(r'^legal$', newsletter_views.legal, name='legal'),


    # twilio
    url(r'^sms/$', sms_views.sms, name='sms'),

    # ajax profile
    url(r'^profile/take$', profile_views.ajax_take, name='ajax_take'),
    url(r'^profile/complete$', profile_views.ajax_complete, name='ajax_complete'),
    url(r'^profile/dropbox$', profile_views.ajax_connect_dropbox, name='ajax_dropbox'),

]


if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT);
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
