#!/usr/bin/python3
from .models import *


def main():
    # Create a new record using the model's constructor.
    output=""
    if not Categories.objects.filter(category='inne').count():
        record = Categories(category='inne')
        record.save()
    
    all_records = Categories.objects.all()
    output.append(all_records)
    
    record = Journal(login='Jarek', value=100, category=Categories.objects.get(category='inne'), description='Test')
    record.save()
    
    
    all_records = Journal.objects.all()
    output.append(all_records)
    
    return output
    

if __name__ == '__main__':
    
    main()
  










