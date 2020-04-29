#!/usr/bin/python3
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def main():

    output=[]
    try:
        
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor() 
        cursor.execute("CREATE TABLE IF NOT EXISTS vendors (vendor_id SERIAL PRIMARY KEY, vendor_name VARCHAR(255) NOT NULL);")
        conn.commit()
        cursor.execute('INSERT INTO vendors(vendor_name) VALUES(%s);', ('Jarek3',))
        conn.commit()
        cursor.execute("SELECT * FROM vendors;")
        #record = cursor.fetchone() 
        records = cursor.fetchall()
        
        for line in records:
            output.append(line)
            
    except (Exception, psycopg2.Error) as error : 
        print ("Error while connecting to PostgreSQL", error)
    finally: 
        #closing database conn. 
        if(conn): 
            cursor.close() 
            conn.close() 
            print("PostgreSQL conn is closed") 
        
    return str(output)
if __name__ == '__main__':
    
    main()
  










