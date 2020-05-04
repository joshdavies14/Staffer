from django.http import HttpRequest, HttpResponseRedirect
from datetime import datetime, time, timedelta, date
from django.template import RequestContext
from django.db import connection
from collections import namedtuple
from django.contrib import messages
import random

def allocate(request, swap, swap_id):
    total_allocated = 0
    """Allocates shifts when admin presses button"""
    assert isinstance(request, HttpRequest)
    user_id = int(request.user.id)

    with connection.cursor() as cursor:
        if swap == True:
            allocate2_query = """SELECT id, shift_name, shift_date, shift_worker, shift_start, shift_end FROM staffer_shift WHERE id = '{}'""".format(swap_id)
            cursor.execute(allocate2_query)
            allocate_data = cursor.fetchall()
        else:
            allocate_query = """SELECT id, shift_name, shift_day, staff_limit, shift_starttime, shift_endtime, allocated FROM staffer_shifttemplate where allocated = 'False'"""
            cursor.execute(allocate_query)
            allocate_data = cursor.fetchall()
        ##print(allocate_data)

        staff_query = """SELECT id FROM auth_user where username != 'admin'"""

        cursor.execute(staff_query)
        staff_data = cursor.fetchall()

        ti = time(12, 0)

        ##print(ti)
        print("len allocate {}".format(len(allocate_data)))
        for i in range(0, len(allocate_data)):
            for y in range(allocate_data[i][3]):
                ##print("i: {}".format(i))
                av_users = []
                pref_array = []
                day_code2 = ""
                ##get day of date in int form +1 to match database
                day_code = (datetime.weekday(allocate_data[i][2]))
                print(day_code)
                if day_code == 0:
                    day_code = "mon"
                elif day_code == 1:
                    day_code = "tues"
                elif day_code == 2:
                    day_code = "wed"
                elif day_code == 3:
                    day_code = "thurs"
                elif day_code == 4:
                    day_code = "fri"
                elif day_code == 5:
                    day_code = "sat"
                elif day_code == 6:
                    day_code = "sun"
                ##work out what pref needs to be compared
                if allocate_data[i][4] < ti and allocate_data[i][5] < ti:
                    ##print("AM shift")
                    shift = "AM"
                elif allocate_data[i][4] > ti and allocate_data[i][5] > ti:
                    ##print("PM shift")
                    shift = "PM"
                else:
                    ##print("All Day shift")
                    shift = "All Day"
                ##select all users
                ##identify which ones have that shift in preference / all day
                ##print("len staff {}".format(len(staff_data)))
                for x in range(len(staff_data)):
                    pref_query = """SELECT {}AM, {}PM FROM staffer_shiftpreference WHERE user_id = {} ORDER BY user_id, id DESC LIMIT 1""".format(day_code, day_code, staff_data[x][0])
                    ##print(pref_query)
                    cursor.execute(pref_query)
                    pref_data2 = cursor.fetchall()
                    ##print(pref_data2)
                    for a in range(len(pref_data2)):
                        pref_array.append(pref_data2[a][0])
                        ##print(pref_data2[i][0])
                        if pref_data2[a][0] == pref_data2[a][1] and (pref_data2[a][0] >= 3 or pref_data2[a][1] >= 3):
                            pref_array[a] = "All Day"
                        elif pref_data2[a][0] >= pref_data2[a][1]:
                            pref_array[a] = "AM"
                        elif pref_data2[a][1] >= pref_data2[a][0]:
                            pref_array[a] = "PM"
                    if len(pref_data2) > 0:
                        sft = pref_array[0]
                        ##print(pref_data2)
                        ##print(sft)
                        if sft == shift or sft == "All Day":
                            av_users.append(staff_data[x][0])
                            print(av_users)
                if len(av_users) == 0:
                    for x in range(len(staff_data)):
                        av_users.append(staff_data[x][0])
                same_shift = []
                print(allocate_data[i][2])
                ss_query = """SELECT shift_worker FROM staffer_shift WHERE shift_date = '{}'""".format(allocate_data[i][2])
                ##print(ss_query)
                cursor.execute(ss_query)
                ss_data = cursor.fetchall()
                ##print(ss_data)
                if len(ss_data) != 0:
                #    for y in range(len(av_users)):
                #        same_shift.append(av_users[y])
                #else:
                    for pi in range(len(ss_data)):
                        if ss_data[pi][0] not in av_users:
                            same_shift.append(ss_data[pi][0])
                print("same-shift", same_shift)
                for d in same_shift:
                    if d in av_users:
                        av_users.remove(d)
                print(av_users)
                if day_code == "mon":
                    mon = allocate_data[i][2] - timedelta(days=0)
                    sun = allocate_data[i][2] + timedelta(days=6)
                elif day_code == "tues":
                    mon = allocate_data[i][2] - timedelta(days=1)
                    sun = allocate_data[i][2] + timedelta(days=5)
                elif day_code == "wed":
                    mon = allocate_data[i][2] - timedelta(days=2)
                    sun = allocate_data[i][2] + timedelta(days=4)
                elif day_code == "thurs":
                    mon = allocate_data[i][2] - timedelta(days=3)
                    sun = allocate_data[i][2] + timedelta(days=3)
                elif day_code == "fri":
                    mon = allocate_data[i][2] - timedelta(days=4)
                    sun = allocate_data[i][2] + timedelta(days=2)
                elif day_code == "sat":
                    mon = allocate_data[i][2] - timedelta(days=5)
                    sun = allocate_data[i][2] + timedelta(days=1)
                elif day_code == "sun":
                    mon = allocate_data[i][2] - timedelta(days=6)
                    sun = allocate_data[i][2] + timedelta(days=0)
                ##print(mon, sun)
                week_query = """SELECT shift_worker, shift_start, shift_end FROM staffer_shift WHERE (shift_date BETWEEN '{}' AND '{}') """.format(mon, sun)
                cursor.execute(week_query)
                week_data = cursor.fetchall()
                id_array = []
                ##print(week_data)
                user_list = []
                for beta in range(len(week_data)):
                    if week_data[beta][0] not in user_list:
                        user_list.append(week_data[beta][0])
                #get all user id in list
                for delta in range(len(user_list)):
                    ##print("delta", delta)
                    week2 = week_data
                    id_count = 0
                    for alpha in range(len(week2)):
                        ##print("alpha", alpha)
                        ##print(alpha)
                        ##print(week_data)
                        
                        #find total hours for each user within list
                        if len(week2) != 0:
                            if week2[alpha][0] == user_list[delta]:
                                dateTimeA = datetime.combine(date.today(), week2[alpha][2])
                                dateTimeB = datetime.combine(date.today(), week2[alpha][1])
                                dateTimediff = dateTimeA - dateTimeB
                                temp = dateTimediff.total_seconds() / 3600
                                print("abs", abs(temp))
                                id_count += abs(temp)
                                print(id_count)
                                week2 = week2[ : alpha] + ((0,0), ) + week2[alpha+1 : ]
                    id_array.append(id_count)
                for kappa in range(len(staff_data)):
                    if staff_data[kappa][0] not in user_list:
                        user_list.append(staff_data[kappa][0])
                        id_array.append(0)
                ##print(user_list)
                ##print(id_array)

                #for gamma in range(len(user_list)):
                #    if user_list[gamma] in same_shift:
                #        same_shift.remove(user_list[gamma])
                print(av_users)
                if len(id_array) > 0 and len(same_shift) == 0:
                    print("if")
                    max_count = id_array[0]
                    max_worker = user_list[0]
                    for count in range(len(id_array)):
                        #print(id_array[count])
                        if id_array[count] <= max_count:
                            max_count = id_array[count]
                            max_worker = user_list[count]
                        #print(max_worker)
                    
                    sort_id_array = {}
                    for idnum in range(len(id_array)):
                        sort_id_array[user_list[idnum]] = id_array[idnum]

                    print(sort_id_array)

                    id_array_sorted = {k: v for k, v in sorted(sort_id_array.items(), key=lambda item: item[1])}

                    print(id_array_sorted)
                    new_id_dict = {}
                    if len(av_users) > 0:
                        for key in id_array_sorted.keys():
                            if key in av_users:
                                new_id_dict[key] = id_array_sorted[key]
                        print(new_id_dict)
                    else:
                        new_id_dict = id_array_sorted
                    rep_result = ""

                    while rep_result == "":
                        for xalpha in new_id_dict.keys():
                            for yalpha in new_id_dict.keys():
                                print(xalpha, yalpha)
                                if new_id_dict[xalpha] == new_id_dict[yalpha]:
                                    rep_result = check_reputation(xalpha, yalpha)
                                    break
                                elif new_id_dict[xalpha] == 0:
                                    rep_result = xalpha
                                    break
                                elif new_id_dict[yalpha] == 0:
                                    rep_result = yalpha
                                    break
                                elif (new_id_dict[xalpha] - 5) <= new_id_dict[yalpha] <= (new_id_dict[xalpha] + 5):
                                    rep_result = check_reputation(xalpha, yalpha)
                                    break
                    print("rep result", rep_result)
                    max_worker = rep_result


                else:
                    print("else")
                    ran_num = random.randint(0, (len(same_shift)-1))
                    max_worker = av_users[ran_num]
                print("worker", max_worker)
                hours_query = """SELECT hours from staffer_userinfo WHERE staff_id = '{}'""".format(max_worker)
                cursor.execute(hours_query)
                hours = cursor.fetchall()
                print(hours)
                hours = hours[0][0]
                dateTimeA = datetime.combine(date.today(), allocate_data[i][4])
                dateTimeB = datetime.combine(date.today(), allocate_data[i][5])
                dateTimediff = dateTimeA - dateTimeB
                hours += abs(dateTimediff.total_seconds() / 3600)
                update_query = """UPDATE staffer_userinfo SET hours = '{}' WHERE staff_id = '{}'""".format(hours, max_worker)
                cursor.execute(update_query)
                ##print(max_worker)
                ##ran_num = random.randint(0, (len(same_shift)-1))
                ##print(len(same_shift))
                ##print(ran_num)
                if swap == True:
                    update_query = """UPDATE staffer_shift SET shift_worker = '{}' WHERE id = '{}'""".format(max_worker, swap_id)
                    cursor.execute(update_query)
                else:
                    add_query = """INSERT INTO staffer_shift (shift_date, shift_start, shift_end, shift_worker, shift_name, template_id)
                    VALUES('{}', '{}', '{}', {}, '{}', {})""".format(allocate_data[i][2], allocate_data[i][4], allocate_data[i][5], max_worker, allocate_data[i][1], allocate_data[i][0])
                    ##print(add_query)
                    cursor.execute(add_query)
                    end_query = """UPDATE staffer_shifttemplate SET allocated = 1 WHERE id = {}""".format(allocate_data[i][0])
                    ##cursor.execute(end_query)
                
            
            total_allocated += 1
    if len(allocate_data) == 0:
        ##print("No shifts to allocate")
        messages.error(request, "No shifts to allocate")
    elif swap == True:
        messages.info(request, "Shift swapped")
    else:
        ##print("All shifts allocated")
        messages.success(request, "{} shift(s) allocated".format(total_allocated))

def check_reputation(val1, val2):
    check_query = """SELECT rep_score FROM staffer_userinfo WHERE staff_id = {}""".format(val1)
    check_query2 = """SELECT rep_score FROM staffer_userinfo WHERE staff_id = {}""".format(val2)
    with connection.cursor() as cursor:
        cursor.execute(check_query)
        check1 = cursor.fetchall()
        cursor.execute(check_query2)
        check2 = cursor.fetchall()
    if check1[0][0] > check2[0][0]:
        return val1
    elif check1[0][0] < check2[0][0]:
        return val2
    else:
        return val1