#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests
import re
import sys
import threading
from queue import Queue
import time
import unidecode
import pickle

THREADS=3
moviesAllData=[]
lock = threading.Lock()

preHtml="""
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="style.css" media="screen, projection">
</head>
<body>
<div class="divTable" style="border: 1px solid #000;">
<div class="divTableBody">
"""
postHtml="""
</div>	
</div>	
</body>
</html>
"""

def getTitles():
    '''returns generator with titles from movie toplist on piratebay and corresponding Imdb search links'''

    try: 
        resp = requests.get('https://thepiratebay.org/top/201')
        soup = BeautifulSoup(resp.text,features="html.parser")
        filmList = soup.find('table',attrs={'id':'searchResult'})
        links = filmList.find_all('a',attrs={'class':'detLink'})
    except:
        print('Unidentified problem with initial scraping piratebay page')
        exit(1)
    pattern=re.compile(r'(HDRip|XviD|AC3-EVO|HDCAM|WEB-DL|\(|\))',re.IGNORECASE) #helps to filter out some piratebay title text

    for index,link in enumerate(links):
        if index > 15: break
        try:
            piratebayTitle = link.text
            if re.search(r'hdcam',piratebayTitle.lower()): continue
            title = pattern.sub('',piratebayTitle)
            year = re.findall(r'2[0-9]{3}',title)[0]
            title = re.split(r'2[0-9]{3}',title)[0]
            title = title.replace('.',' ').strip()+' '+year
            imdbUrl = 'https://www.imdb.com/find?q={}&ref_=nv_sr_sm'.format(title.replace(' ','+'))
            
            yield index,title,piratebayTitle,imdbUrl
            
        except:
            print('Problem with parsing piratebay titles and links')
            exit(1)

def checkImdb(q):
    '''prints imdb details for specific title/url'''
    
    global moviesAllData
    while not q.empty():
        
        index,title,piratebayTitle,imdbUrl = q.get()
        
        #find link to movie page
        try:
            resp = requests.get(imdbUrl)
            soup = BeautifulSoup(resp.text,features="html.parser")
            table = soup.find('table',attrs={'class':'findList'})
            movieUrlPart = table.find('a')['href']
        except:
            print('Problem with initial title search on imdb: {}'.format(title))
        
        #get data from movie page
        try:
            resp = requests.get('https://www.imdb.com'+movieUrlPart)
            soup = BeautifulSoup(resp.text,features="html.parser")
            imdbTitle = soup.find('div',attrs={'class':'title_wrapper'}).find('h1').text.strip()
            imdbTitle = unidecode.unidecode(imdbTitle)
            rating = soup.find('span',attrs={'itemprop':'ratingValue'}).text
            votes = soup.find('span',attrs={'itemprop':'ratingCount'}).text
            genreSoup = soup.find('div',attrs={'class':'subtext'})
            genreLinks = genreSoup.find_all('a')
            genre='('+','.join([link.text for link in genreLinks if 'genres' in str(link)])+')'
            summary = soup.find('div',attrs={'class':'summary_text'}).text.strip()
            summary = unidecode.unidecode(summary)
           
            print('#{}: IMDB title: {}, rating: {}, votes: {}, genre:{}, Piratebay title: {}'.\
                 format(index,imdbTitle,rating,votes,genre,piratebayTitle))
            
            lock.acquire()
            moviesAllData.append({'imdbTitle':imdbTitle,
                                  'rating':rating,
                                  'votes':votes,
                                  'genre': genre,
                                  'piratebayTitle':piratebayTitle,
                                  'summary': summary})
            lock.release()
            
        except Exception as e:
            print('#{}: Did not find data on imdb for movie: {}'.format(index,title))
            #print(e.message, e.args)

        q.task_done()
        


def timeIt(func):
    """simple task duration counter"""
    def wrapper(*args, **kwargs): 
        startTime = time.time() 
        func(*args, **kwargs) 
        endTime = time.time() 
        print('Time taken:', endTime - startTime, 'seconds')
    return wrapper 

def saveLastSearch(sortedMovies):
    """saves search results as text and as pickled dictionary"""
    with open ('checkFilms.txt','w') as file:
        for movie in sortedMovies:
            file.write("Rating: {}, votes total: {}, genre:{}, IMDB title: {}, piratebay title: {}\r\n".\
              format(movie['rating'], movie['votes'],movie['genre'],movie['imdbTitle'], movie['piratebayTitle']))
    with open ('checkFilms.dat','wb') as file:
        file.write(pickle.dumps(sortedMovies))

def lastSearchText():
    """saves last search results as text"""
    try:
        with open ('checkFilms.txt','r') as file:
            lines = str(file.read())
    except FileNotFoundError: 
        lines=""
    return lines

def lastSearchPickled():
    """saves last search results as pickled dictionary"""
    with open ('checkFilms.dat','rb') as file:
        sortedMovies = pickle.loads(file.read())
    return sortedMovies

def displaySorted(sortedMovies):
    """displays search results from input dictionary"""
    print(preHtml)
    for movie in sortedMovies:
        
        if movie['imdbTitle'] not in lastSearchText(): b,be='<b>','</b>'
        else:                                             b,be='',''
            
        print('<div class="divTableRow">')
        print("""<div class="divTableCell">Rating: {}</div> 
              <div class="divTableCell">votes total: {}</div>
              <div class="divTableCell">genre:{}</div>
              <div class="divTableCell" title="{}">{}IMDB title: {}{}</div>
              <div class="divTableCell">piratebay title: {}</div>""".\
              format(movie['rating'], movie['votes'],movie['genre'],movie['summary'],b,movie['imdbTitle'],be, movie['piratebayTitle']))
        if movie['imdbTitle'] not in lastSearchText(): print("</b>")
        print('</div>')
         
    print(postHtml)

            
@timeIt
def main():
    
    if len(sys.argv) > 1:        #show only last search from pickled dictionary in checkFilms.dat
        if sys.argv[1] == 'showLastSearch':
            displaySorted(lastSearchPickled())
            exit(0)
    
    jobs = Queue()
    for entry in getTitles(): #add titles to queue
        jobs.put(entry)
    
    for i in range(THREADS):  #create threads
        worker = threading.Thread(target=checkImdb, args=(jobs,))
        worker.start()

    print("<b>Starting imdb check for {} piratebay movies in {} threads. At the and sorted list will be presented.</b>".\
          format(jobs.qsize(),THREADS))
    jobs.join()
    
    print('\r\n<b>List of piratebay movies, sorted by imdb rating:</b>')  
    
    sortedMovies = sorted(moviesAllData, key = lambda i: i['rating'])
    displaySorted(sortedMovies)
    saveLastSearch(sortedMovies)
    
if __name__ == '__main__':
    
    main()
  










