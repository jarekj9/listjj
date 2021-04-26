import pyodbc 
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=y4r3k.boo.pl;"
                      "Database=baza;"
                      "Trusted_Connection=yes;")


cursor = cnxn.cursor()
cursor.execute('SELECT * FROM Table')

for row in cursor:
    print('row = %r' % (row,))
