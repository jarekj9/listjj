#!/usr/bin/python3
from .models import *
from django.contrib.auth.models import User

def show_notes(login, startdate, stopdate):
    '''Returns list of dicts with notes for specific user'''
    output=[]

    all_records = Journal.objects.filter(login=login,date__range=(startdate,stopdate)).order_by('date')
    for item in all_records:
        output.append({'id':item.id,
                       'login':item.login.username,  #related object
                       'date':item.date.strftime("%d-%m-%Y"),
                       'value':item.value,
                       'category':item.category.category,  #related object
                       'description':item.description})
    
    return output
    
def page_summary(notes):
    '''Counts summary for specific notes from def "show_notes" '''
    valuesum = sum([item.get('value') for item in notes])

    return valuesum













