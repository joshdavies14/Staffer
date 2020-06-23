"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from Staffer.models import ShiftPreference
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.template import RequestContext

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class UserCreate(UserCreationForm):
    username = forms.CharField()
    password1 = forms.CharField(widget = forms.PasswordInput())
    password2 = forms.CharField(widget = forms.PasswordInput())

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput())

class changePwForm(forms.Form):
    #username = user.username
    #currentpw = user.password
    oldpw = forms.CharField(widget = forms.PasswordInput())
    newpw1 = forms.CharField(widget = forms.PasswordInput())
    newpw2 = forms.CharField(widget = forms.PasswordInput())

class shiftPrefForm(forms.Form):
    monAM = forms.IntegerField()
    monPM = forms.IntegerField()
    tuesAM = forms.IntegerField()
    tuesPM = forms.IntegerField()
    wedAM = forms.IntegerField()
    wedPM = forms.IntegerField()
    thursAM = forms.IntegerField()
    thursPM = forms.IntegerField()
    friAM = forms.IntegerField()
    friPM = forms.IntegerField()
    satAM = forms.IntegerField()
    satPM = forms.IntegerField()
    sunAM = forms.IntegerField()
    sunPM = forms.IntegerField()

class ShiftPref(ModelForm):
    class Meta:
        model = ShiftPreference
        fields = ['user_id', 'day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7']

class newShiftForm(forms.Form):
    shiftName = forms.CharField()
    shiftDate = forms.DateField()
    shiftStart = forms.TimeField()
    shiftEnd = forms.TimeField()
    shiftLimit = forms.IntegerField()

class AddUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    is_superuser = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_superuser')

class changeRepForm(forms.Form):
    user_pick = forms.CharField()
    rep1ontime = forms.IntegerField()
    rep2uniform = forms.IntegerField()
    rep3additional = forms.IntegerField()