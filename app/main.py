#!/usr/bin/python3
from .models import *
from django.contrib.auth.models import User
import csv
from django.http import HttpResponse

def show_notes(login, filter):
    '''Returns list of dicts with notes for specific user'''
    output=[]

    if not filter['category']: filter['category'] = Categories.objects.all()

    all_records = Journal.objects.filter(login = login,
                                         date__range = (filter['startdate'],filter['stopdate']),
                                         category__in = filter['category']).order_by('date')
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

def export_data(login):

    csv_response = HttpResponse(content_type='text/csv')
    csv_response['Content-Disposition'] = 'attachment; filename="export.csv"'
    all_records = Journal.objects.filter(login = login)
    
    for item in all_records:
        one_row_tab = [item.id, item.login.username, item.date, item.value, 
               item.category.category, item.description]
        writer = csv.writer(csv_response)
        writer.writerow(one_row_tab)

    return csv_response









