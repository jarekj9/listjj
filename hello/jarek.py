#!/usr/bin/python3
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def main():
    
    try: 
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = connection.cursor() 
        cursor.execute("CREATE TABLE vendors \
              (vendor_id SERIAL PRIMARY KEY, vendor_name VARCHAR(255) NOT NULL);")
        
        cursor.execute('INSERT INTO vendors(vendor_name) \
                        VALUES("Jarek");') 
        cursor.execute("SELECT * FROM vendors;")
        record = cursor.fetchone() 
        return str(record)
    except (Exception, psycopg2.Error) as error : 
        print ("Error while connecting to PostgreSQL", error) 
    finally: 
        #closing database connection. 
            if(connection): 
                cursor.close() 
                connection.close() 
                print("PostgreSQL connection is closed") 
if __name__ == '__main__':
    
    main()
  










