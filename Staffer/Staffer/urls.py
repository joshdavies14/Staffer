"""
Definition of urls for Staffer.
"""

from datetime import datetime
from django.conf.urls import url, include
from django.urls import path
import django.contrib.auth.views as auth_views
import app.forms
import app.views
from app.views import dashboard, change_pw, privacy, shiftpref_submit, allocate_shift, adm, admin_users, admin_view_shifts, admin_add_shift, login_view, swap_shift, changerep
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', app.views.login_view, name='home'),
    url(r'^home$', app.views.home, name='home'),
    url(r'^contact$', app.views.contact, name='contact'),
    url(r'^about$', app.views.about, name='about'),
    url(r'^accounts/login/go/$', app.views.user_login, name='login'),
    url(r'^accounts/login/$', app.views.login_view, name='login'),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(template_name='app/logout.html'), {'next_page': '/',}, name='logout'),
    url(r'^accounts/changepw/$', app.views.change_pw, name='changepw'),
    url(r'^dashboard/$', app.views.dashboard, name='dashboard'),
    url(r'^dashboard/settings/', app.views.usersettings, name='settings'),
    url(r'^dashboard/calendar/', app.views.calendar, name='calendar'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^password/$', app.views.change_pw, name='change_pw'),
    url(r'^privacy/$', app.views.privacy, name='privacy'),
    url(r'^submit/shiftpref/$', app.views.shiftpref_submit, name='prefform'),
    url(r'^dashboard/admin/shifts/allocate/$', app.views.allocate_shift, name='allocate'),
    url(r'^dashboard/admin/$', app.views.adm, name='admin'),
    url(r'^dashboard/admin/users/$', app.views.admin_users, name='admin-users'),
    url(r'^dashboard/admin/shifts/add/$', app.views.admin_add_shift, name='admin_add_shift'),
    url(r'^dashboard/admin/shifts/$', app.views.admin_view_shifts, name='admin-view-shifts'),
    url(r'^submit/newshift/$', app.views.add_shift, name='createshift'),
    url(r'^dashboard/admin/users/new/$', app.views.newUserView, name='newuser'),
    path('submit/swapshift/<int:shiftid>/', app.views.swap_shift, name='swap'),
    url(r'^submit/reputation/$', app.views.changerep, name='changerep'),
]
