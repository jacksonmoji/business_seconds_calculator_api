from __future__ import unicode_literals
from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import list_route, api_view
from rest_framework.parsers import  JSONParser
from django.shortcuts import render
from datetime import datetime,timedelta
import time
import requests
import json
import re

@api_view(['GET', ])
def getDuration(request):

    #retrieving a json list of public holidays from calendarific.com for free, however i can only fetch 1k times a day, just a quick fix.
    url = 'https://calendarific.com/api/v2/holidays?&api_key=0dbc436c7aa0a6899771f096814ded6fc820c5fb2bdf1854ad0eac5705f9e124&country=ZA&year=2019'
    
    response = requests.get(url)
    jsons = json.loads(response.text)
    is_holiday = False

    try:
        try:
            start_time = request.GET['start_time']
            end_time = request.GET['end_time']  
        except:
            return Response({   
            'status': 'Error',
            'message': "Please make sure your parameters variable are correct [start_time] [end_time]"
        }, status=status.HTTP_400_BAD_REQUEST)

        date_obj = datetime.now()
        date_str = date_obj.strftime("%Y-%m-%d")
        day = date_obj.strftime('%A')

        for holidays in jsons["response"]["holidays"]:
            if holidays["date"]["iso"] == date_str:
                is_holiday = True
                break
            else:
                continue

        if is_holiday:
            seconds = 0
        elif day == 'Saturday' or day == 'Sunday':
            seconds = 0            
        else:
            seconds = calcNumberOfSec(start_time,end_time)

    except ValueError as e:
        return Response({
        'status': 'Error',
        'message':'{}'.format(e)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(seconds)


def calcNumberOfSec(start_time,end_time):
   
    try:
        x1 = time.strptime(start_time, '%H:%M')
        x2 = time.strptime(end_time, '%H:%M')

    except ValueError as e:
        return Response({
            'status': 'Error',
            'message': '{}'.format(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    tx1 = timedelta(hours=x1.tm_hour,minutes=x1.tm_min)
    tx2 = timedelta(hours=x2.tm_hour,minutes=x2.tm_min)
    print(checkAllowedHours(tx1,tx2))
    
    if checkAllowedHours(tx1,tx2):

        if tx1 < tx2:
            start_time = int(timedelta(hours=x1.tm_hour,minutes=x1.tm_min).total_seconds())
            end_time = int(timedelta(hours=x2.tm_hour,minutes=x2.tm_min).total_seconds())
        
            total =  end_time - start_time
        else:
    
            raise Exception("start_time cannot be greater than end_time")
    else:

        raise Exception("Times out of working hours bounds, working hours are between 08:00 and 17:00 weekly")
    
    return total

def checkAllowedHours(start_time,end_time):
    
    l_start = int(re.sub(r":", '', str(start_time)))
    l_end = int(re.sub(r":", '', str(end_time)))

    business_time_start = 80000
    business_time_end = 170000

    if (l_end > business_time_end) or (l_start < business_time_start):
        return False
    else:
        return True