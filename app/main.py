#!/usr/bin/python3
from .models import *


def main():
    # Create a new record using the model's constructor.
    record = Journal(login='Jarek', value=100, description='Test')

    # Save the object into the database.
    record.save()
    
    
    all_records = Journal.objects.all()
    
    for line in all_records:
        print(line)
    
    

if __name__ == '__main__':
    
    main()
  










