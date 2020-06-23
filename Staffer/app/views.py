"""
Definition of views.
"""

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseRedirect
from django.template import RequestContext
from datetime import datetime, time
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.urls import reverse_lazy
from .forms import LoginForm, shiftPrefForm, ShiftPref, newShiftForm, AddUserForm, changePwForm, changeRepForm
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.core.mail import send_mail
from django.db import connection
from Staffer.models import ShiftPreference, Shift, ShiftTemplate
from collections import namedtuple
from django.contrib.auth.models import User
import random
import Staffer.allocate as allocate

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact Us',
            'message':'Questions? Ask us!',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About Staffer',
            'message':'All about Staffer',
            'year':datetime.now().year,
        }
    )

@login_required
def dashboard(request):
    """Renders the user portal page."""
    assert isinstance(request, HttpRequest)
    user_id = int(request.user.id)
    with connection.cursor() as cursor:
        def namedtuplefetchall(cursor):
            "Return all rows from a cursor as a namedtuple"
            desc = cursor.description
            nt_result = namedtuple('Result', [col[0] for col in desc])
            return [nt_result(*row) for row in cursor.fetchall()]
        query = """SELECT shift_date, shift_start, shift_end FROM staffer_shift where shift_worker = {}""".format(user_id)
        query2 = """SELECT id, shift_date, shift_start, shift_end FROM staffer_shift WHERE shift_date >= CURDATE() AND shift_worker = '{}' ORDER BY shift_date""".format(user_id)
        ##print(query2)
        cursor.execute(query2)
        data = cursor.fetchall()
        ##print(data)
        shift_data = []
        shift_array = []
        if data:
            for i in range(4):
                shift_data.append(data[0][i])
            ##print(shift_data)
            for i in range(4):
                var = shift_data[i]
                shift_array.append(var)
            print(shift_array)
            context = {
                'shift_date': shift_array[1], 'shift_start': shift_array[2], 'shift_end': shift_array[3], 'shift_id': shift_array[0] ,'array': 'true',
            }   
        else:
            context = {'array': 'False',}
    ##print(context)
    ##allocate_shift(request)
    return render(request, 'app/dashboard/dashboard.html', context)

@login_required
def usersettings(request):
    """Renders the user settings page."""
    assert isinstance(request, HttpRequest)
    user_id = int(request.user.id)
    ShiftPreference.objects.raw('SELECT * FROM staffer_shiftpreference WHERE user_id = %s',[user_id])
    with connection.cursor() as cursor:
        def namedtuplefetchall(cursor):
            "Return all rows from a cursor as a namedtuple"
            desc = cursor.description
            nt_result = namedtuple('Result', [col[0] for col in desc])
            return [nt_result(*row) for row in cursor.fetchall()]
        query = """SELECT monAM, monPM, tuesAM, tuesPM, wedAM, wedPM, thursAM, thursPM, friAM, friPM, satAM, satPM, sunAM, sunPM FROM staffer_shiftpreference WHERE user_id = {} ORDER BY user_id, id DESC LIMIT 1""".format(user_id)
        cursor.execute(query)
        data = namedtuplefetchall(cursor)
        ##print(data)
        day_array = []
        print(day_array)
        if data:
            print("if")
            for i in range(14):
                day_array.append(data[0][i])
                ##print("data appended")
            print(day_array)
            context = {
                'monAM': day_array[0], 'monPM': day_array[1], 'tuesAM': day_array[2], 'tuesPM': day_array[3], 'wedAM': day_array[4], 'wedPM': day_array[5], 'thursAM': day_array[6], 'thursPM': day_array[7], 'friAM': day_array[8], 'friPM': day_array[9], 'satAM': day_array[10], 'satPM':day_array[11], 'sunAM': day_array[12], 'sunPM': day_array[13]
            }
            shiftform = shiftPrefForm()
            
        else:
            print("else")
            context = {
                'monAM': 'Not Set', 'monPM': 'Not Set', 'tuesAM': 'Not Set', 'tuesPM': 'Not Set', 'wedAM': 'Not Set', 'wedPM': 'Not Set', 'thursAM': 'Not Set', 'thursPM': 'Not Set', 'friAM': 'Not Set', 'friPM': 'Not Set', 'satAM': 'Not Set', 'satPM': 'Not Set', 'sunAM': 'Not Set', 'sunPM': 'Not Set'
            }
        return render(request, 'app/dashboard/settings.html', context)
    
@login_required
def calendar(request):
    """Renders the user calendar page."""
    assert isinstance(request, HttpRequest)
    user_id = int(request.user.id)
    userquery = """select id, shift_name, shift_date, shift_start, shift_end from staffer_shift WHERE shift_date >= CURDATE() and shift_worker = '{}';""".format(user_id)
    with connection.cursor() as cursor:
        cursor.execute(userquery)
        ##query_results = Shift.objects.filter(shift_worker=user_id)
        query_results = cursor.fetchall()
    context = {'query_results': query_results}
    return render(request, 'app/dashboard/calendar.html', context)

def user_login(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        ##print("form valid")
        userObj = form.cleaned_data
        ##print(userObj)
        username = userObj['username']
        password = userObj['password']
        ##print(username, password)
        user = authenticate(request, username=username, password=password)
        ##print(user)
        if user is not None:
            login(request, user)
            ##return render(request, 'app/dashboard.html', {})
            if username == 'admin':
                return HttpResponseRedirect('/dashboard/admin')
            else:
                return HttpResponseRedirect('/dashboard')
        else:
            messages.error(request, "Sorry, that login was invalid. Please try again.")
            ##return render(request, 'app/index.html', {})
            return HttpResponseRedirect('/')
    else:
        messages.error(request, "Sorry, that login was invalid. Please try again.")
        return HttpResponseRedirect('/')

@login_required
def shiftpref_submit(request):
    form = shiftPrefForm(request.POST)
    ##print(form)
    current_user = request.user
    ##print(request.user.id)
    user_id = int(request.user.id)
    if form.is_valid():
        userObj = form.cleaned_data
        ##print("form valid")
        monAM = int(userObj['monAM'])
        monPM = int(userObj['monPM'])
        tuesAM = int(userObj['tuesAM'])
        tuesPM = int(userObj['tuesPM'])
        wedAM = int(userObj['wedAM'])
        wedPM = int(userObj['wedPM'])
        thursAM = int(userObj['thursAM'])
        thursPM = int(userObj['thursPM'])
        friAM = int(userObj['friAM'])
        friPM = int(userObj['friPM'])
        satAM = int(userObj['satAM'])
        satPM = int(userObj['satPM'])
        sunAM = int(userObj['sunAM'])
        sunPM = int(userObj['sunPM'])
        #user_id = 2
        #day1, day2, day3, day4, day5, day6, day7 = 11, 22, 33, 44, 55, 66, 77
        with connection.cursor() as cursor:
            sql_query = """ INSERT INTO staffer_shiftpreference (user_id, monAM, monPM, tuesAM, tuesPM, wedAM, wedPM, thursAM, thursPM, friAM, friPM, satAM, satPM, sunAM, sunPM)
            VALUES({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})""".format(user_id, monAM, monPM, tuesAM, tuesPM, wedAM, wedPM, thursAM, thursPM, friAM, friPM, satAM, satPM, sunAM, sunPM)
            #sql_query2 = """INSERT INTO staffer_shiftpreference (user_id, day1, day2, day3, day4, day5, day6, day7)
            #VALUES(2, 0, 1, 2, 0, 3, 1, 2)"""
            cursor.execute(sql_query)
            print("query complete")
        messages.success(request, "Shift preferences saved!")
        return HttpResponseRedirect('/dashboard')

@login_required
def change_pw(request):
    form = changePwForm(request.POST)
    if form.is_valid():
        formObj = form.cleaned_data
        if formObj['newpw1'] == formObj['newpw2']:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(formObj['newpw1'])
            u.save()
            messages.success(request, "Password successfully changed")
        else:
            messages.error(request, "Passwords do not match")
    else:
        messages.error(request, "Form invalid: lease try again")
    return HttpResponseRedirect('/dashboard')

def privacy(request):
    """Renders the privacy policy page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/privacy.html',
        {
            'title':'Privacy Policy',
            'year':datetime.now().year,
        }
    )

@login_required
def allocate_shift(request):
    allocate.allocate(request, False, 0)
    return HttpResponseRedirect('/dashboard/admin')

@login_required
def swap_shift(request, shiftid):
    allocate.allocate(request, True, shiftid)
    return HttpResponseRedirect('/dashboard')

@login_required
def adm(request):
    assert isinstance(request, HttpRequest)
    data_array = []
    context = {}
    with connection.cursor() as cursor:
        def namedtuplefetchall(cursor):
            ##Return all rows from a cursor as a namedtuple
            desc = cursor.description
            nt_result = namedtuple('Result', [col[0] for col in desc])
            return [nt_result(*row) for row in cursor.fetchall()]
        query = """select shift_date from staffer_shift  ORDER BY shift_date DESC LIMIT 1 ;"""
        cursor.execute(query)
        data = namedtuplefetchall(cursor)
        print(data)
        if data:
            print("if")
            data_array.append(data[0][0])
            print(data_array)
            context['unallocate_date'] = data_array[0]
        print(context)
        data_array = []
        todayquery = """select id, shift_name, shift_start, shift_end, shift_worker from staffer_shift WHERE shift_date = CURDATE();"""
        cursor.execute(todayquery)
        today_data = cursor.fetchall()
        context['today_data'] = today_data
        unallocatedquery = """SELECT shift_name, shift_day, staff_limit, shift_starttime, shift_endtime FROM staffer_shifttemplate WHERE allocated = 0;"""
        cursor.execute(unallocatedquery)
        unallocated_data = cursor.fetchall()
        context['unallocated_data'] = unallocated_data
    return render(request, 'app/dashboard/admin/admin.html', context)

@login_required
def admin_users(request):
    print("Add user")
    userquery = """SELECT first_name, last_name, username, email, last_login, is_superuser FROM auth_user"""
    with connection.cursor() as cursor:
        cursor.execute(userquery)
        query_results = cursor.fetchall()
    ##print(query_results)
    ##query_results = User.objects.all()
    ##print(User.objects.all())
    context = {'query_results': query_results}
    return render(request, 'app/dashboard/admin/users.html', context)

@login_required
def admin_view_shifts(request):
    user_id = request.user.id
    print("View shift")
    ##calquery = """SELECT shift_name, shift_date, shift_start, shift_end FROM staffer_shift WHERE shift_worker = {}""".format(user_id)
    ##query_results = Shift.objects.all()
    userquery = """select shift_name, shift_date, shift_start, shift_end, shift_worker from staffer_shift WHERE shift_date >= CURDATE();"""
    namequery = """SELECT first_name, last_name FROM auth_user WHERE id = '{}'""".format(user_id)
    with connection.cursor() as cursor:
        cursor.execute(userquery)
        query_results = cursor.fetchall()
        for result in query_results:
            cursor.execute(namequery)
            name_results = cursor.fetchall()

    context = {'query_results': query_results}
    return render(request, 'app/dashboard/admin/shift-view.html', context)

@login_required
def admin_add_shift(request):
    print("Add shift")
    return render(request, 'app/dashboard/admin/shift-add.html')

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/dashboard/')
    else:
        return render(request, 'app/login.html')

@login_required
def add_shift(request):
    form = newShiftForm(request.POST)
    ##print(form.errors)
    if form.is_valid():
        newObj = form.cleaned_data
        print("form valid")
        name = newObj['shiftName']
        date = newObj['shiftDate']
        start = newObj['shiftStart']
        end = newObj['shiftEnd']
        limit = newObj['shiftLimit']
        allocated = 0
        print(name, date, start, end, limit, allocated)
        with connection.cursor() as cursor:
            sql_query = """ INSERT INTO staffer_shifttemplate (shift_name, shift_day, staff_limit, shift_starttime, shift_endtime, allocated)
            VALUES('{}', '{}', {}, '{}', '{}', {})""".format(name, date, limit, start, end, allocated)
            #sql_query2 = """INSERT INTO staffer_shiftpreference (user_id, day1, day2, day3, day4, day5, day6, day7)
            #VALUES(2, 0, 1, 2, 0, 3, 1, 2)"""
            cursor.execute(sql_query)
            print("query complete")
    messages.success(request, "Shift successfully added!")
    return HttpResponseRedirect('/dashboard/admin/')

@login_required
def newUserView(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            newObj = form.cleaned_data
            form.save()
            userQuery = """SELECT id FROM auth_user WHERE username = '{}'""".format(newObj['username'])
            with connection.cursor() as cursor:
                cursor.execute(userQuery)
                userresult = cursor.fetchall()
                user_id = userresult[0][0]
                newInfoQuery = """INSERT INTO staffer_userinfo (staff_id) VALUES ('{}')""".format(user_id)
                cursor.execute(newInfoQuery)
            messages.success(request, "User successfully created!")
            return HttpResponseRedirect('/dashboard/admin')
    else:
        form = AddUserForm
    return render(request, 'app/dashboard/admin/new-user.html', {'form': form})

@login_required
def changerep2(request):
    add_total = 0
    form = changeRepForm(request.POST)
    print(form)
    newObj = form.cleaned_data
    print(newObj)
    if form.is_valid():
        newObj = form.cleaned_data
        form_name = newObj['user_pick']
        name = form_name.split()
        rep1 = newObj['rep1ontime']
        rep2 = newObj['rep2uniform']
        additional = newObj['rep3additional']
        add_total += rep1
        add_total -= rep2
        add_total += additional
        print(name)

@login_required
def changerep(request):
    add_total = 0
    form_name = request.POST.get("userpick")
    rep1 = request.POST.get("rep1ontime")
    rep2 = request.POST.get("rep2uniform")
    additional = int(request.POST.get("rep3additional"))
    if rep1:
        rep1 = int(rep1)
    else:
        rep1 = 0
    if rep2:
        rep2 = int(rep2)
    else:
        rep2 = 0
    name = form_name.split()
    add_total += rep1
    add_total += rep2
    add_total += additional
    name_query = """SELECT id from auth_user WHERE first_name = '{}' and last_name = '{}'""".format(name[0], name[1])
    with connection.cursor() as cursor:
        cursor.execute(name_query)
        name_id = cursor.fetchall()
    print(name_id)
    current_query = """SELECT rep_score FROM staffer_userinfo WHERE staff_id = '{}'""".format(name_id[0][0])
    with connection.cursor() as cursor:
        cursor.execute(current_query)
        current = cursor.fetchall()
        print(current)
    add_total += current[0][0]
    print(add_total)
    update_query = """UPDATE staffer_userinfo SET rep_score = '{}' WHERE staff_id = '{}'""".format(add_total, name_id[0][0])
    with connection.cursor() as cursor:
        cursor.execute(update_query)
    messages.success(request, "User reputation updated")
    return HttpResponseRedirect('/dashboard/admin/')