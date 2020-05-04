#!/usr/bin/python3
from .models import *


def main():

    output=[]
    if not Categories.objects.filter(category='inne').count():
        record = Categories(category='inne')
        record.save()
        
    record = Journal(login='Jarek', value=100, category=Categories.objects.get(category='inne'), description='Test')
    record.save()
    
    
    all_records = Journal.objects.all()
    for item in all_records:
        output.append({'login':item.login,
                       'date':item.date,
                       'value':item.value,
                       'category':item.category.category, #Categories.objects.get(id=item.category.id).category,
                       'description':item.description})
    
    return output
    

if __name__ == '__main__':
    
    main()
  










