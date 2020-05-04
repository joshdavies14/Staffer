"""
Definition of models.
"""

from django.db import models

# Create your models here.
class ShiftTemplate(models.Model):
    id = models.IntegerField(primary_key=True)
    shift_name = models.CharField(max_length=200)
    shift_day = models.DateField()
    staff_limit = models.IntegerField()
    shift_starttime = models.TimeField('start time')
    shift_endtime = models.TimeField('end time')
    allocated = models.BooleanField()
    def __unicode__(self):
        return (self.shift_name)


class ShiftPreference(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    day1 = models.IntegerField()
    day2 = models.IntegerField()
    day3 = models.IntegerField()
    day4 = models.IntegerField()
    day5 = models.IntegerField()
    day6 = models.IntegerField()
    day7 = models.IntegerField()

class Shift(models.Model):
    id = models.IntegerField(primary_key=True)
    shift_date = models.DateField()
    shift_start = models.TimeField('start time')
    shift_end = models.TimeField('end time')
    shift_worker = models.IntegerField()
    shift_name = models.CharField(max_length=200)

class UserInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    staff_id = models.IntegerField()
    rep_score = models.IntegerField()
    staff_level = models.IntegerField()
    hours = models.IntegerField()