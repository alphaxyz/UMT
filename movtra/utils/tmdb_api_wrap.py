#from tmdbv3api import TMDb, Movie, Person
import tmdbsimple as tmdb
import requests
import json
import pprint
import csv
import codecs
import tempfile
import sqlite3
from datetime import datetime
import urllib.request
import os
from os.path import join, dirname
from dotenv import load_dotenv
from pathlib import Path

baseUrl = 'https://api.themoviedb.org/3'
#dotenv_path = join(dirname(__file__), '.env')
current_path = Path(join(dirname(__file__)))
dotenv_path = join(current_path.parent.parent, '.env')
load_dotenv(dotenv_path)
apikey = os.getenv('APIKEY')

def getMovieByID(tmdbID):
	url = baseUrl + '/movie/'+ str(tmdbID) +'?api_key=' + apikey + "&append_to_response=credits"
	if(tmdbID != None):
		json_r = requests.get(url).json()
		movie_info = {}
		movie_info['id']=json_r['id']
		movie_info['adult']=json_r['adult']
		#movie_info['belongs_to_collection']['name'] = json_r['belongs_to_collection']
		#movie_info['belongs_to_collection']=json_r['belongs_to_collection']
		movie_info['budget']=json_r['budget']
		movie_info['homepage']=json_r['homepage']
		movie_info['imdb_id']=json_r['imdb_id']
		movie_info['original_language']=json_r['original_language']
		movie_info['original_title']=json_r['original_title']
		movie_info['overview']=json_r['overview']
		movie_info['popularity']=json_r['popularity']
		movie_info['backdrop_path']=json_r['backdrop_path']
		movie_info['poster_path']=json_r['poster_path']
		movie_info['release_date']=json_r['release_date']
		movie_info['revenue']=json_r['revenue']
		movie_info['runtime']=json_r['runtime']
		movie_info['status']=json_r['status']
		movie_info['tagline']=json_r['tagline']
		movie_info['title']=json_r['title']
		movie_info['video']=json_r['video']
		movie_info['vote_average']=json_r['vote_average']
		movie_info['vote_count']=json_r['vote_count']
		#pprint.pprint(json_r)
		#meglio json_r
		return json_r

def getMovieByName(movieName, pageNumber):
    url = baseUrl + '/search/movie?api_key=' + apikey + '&query=' + movieName +'&page=' + str(pageNumber)
	#+'&year=1967'
    json_r = requests.get(url).json()
    if 'errors' in json_r:
        star = json_r['errors'][0]
        total_pages = [int(s) for s in star.split() if s.isdigit()][0]
        url = baseUrl + '/search/movie?api_key=' + apikey + '&query=' + movieName +'&page=' + str(total_pages)
        json_r = requests.get(url).json()
        
    total_pages =  json_r['total_pages']
    total_results =  json_r['total_results']
    results = json_r['results']
    #pprint.pprint(results)
    return (results, total_pages, total_results)

def getMovieByImdbID(imdbID):
	url = baseUrl + '/find/'+ imdbID +'?api_key='+ apikey +'&external_source=imdb_id'
	json_r = requests.get(url).json()
	tmdbID = json_r['movie_results'][0]['id']

	return getMovieByID(tmdbID)


""" def importImdb(file):
	res = []
	firstline = True
	i = 1
	with codecs.open(file, "r", encoding='utf-8', errors='ignore') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			if firstline:
				firstline = False
				continue
			#res.append(row[1])
			movie = getMovieByImdbID(row[1])
			res.append(movie)
			print(str(i) + ": " +movie['title'])
			i=i+1
	return res
 """

def importImdb(file):
	res = []
	firstline = True
	#i = 1
	with codecs.open(file, "r", encoding='utf-8', errors='ignore') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			if firstline:
				firstline = False
				continue
			#res.append(row[1])
			#movie = getMovieByImdbID(row[1])
			res.append(row[1])
			#print(str(i) + ": " +movie['title'])
			#i=i+1
	return res

def importTest():
	CSV_URL = 'https://www.imdb.com/list/ls072338636/export'

	with requests.Session() as s:
		download = s.get(CSV_URL)
		tmp = open("./temp.csv", "wb")
		#decoded_content = download.content.decode('utf8')
		tmp.write(download.content)
		#decoded_content = download.content.decode('utf-8')

		#cr = csv.readCSV(decoded_content.splitlines(), delimiter=',')
		#my_list = list(cr)
		#for row in my_list:
		#	print(row[1])
		firstline = True
		#with codecs.open(download.content, "r", encoding='utf-8', errors='ignore') as csvfile:
		#	print(20*'-')
			#readCSV = csv.reader(download.content.splitlines(), delimiter=',')
			#for row in readCSV:
			#	if firstline:
			#		firstline = False
			#		continue
			#	print(20*'-')
				#print(row[0])
			#res.append(row[1])
		print('sadasd')

#TODO
def getPersonID(name):
	url = baseUrl + '/search/person?api_key='+ apikey +'&query=quentin%20tarantino'
	return True

def getFilmography(personID):
	url = baseUrl + '/person/'+ str(personID) +'/movie_credits?api_key=' + apikey + '&language=en-US'
	#directing
	#acting
	#writing
	json_r = requests.get(url).json()
	if not 'success' in json_r or json_r['success'] != False:
		cast = {}
		cID = 0
		for c in json_r['cast']:
			if 'release_date' in c:
				rd =  c['release_date']
			else:
				rd = 0
			cast[cID] = {'character': c['character'],
						'poster_path': c['poster_path'],
						'id': c['id'],
						'title': c['title'],
						'release_date': rd
						}
			cID+=1
		crew = {}
		ncrew = {}
		for c in json_r['crew']:
			if not c['job'] in ncrew:
				ncrew[c['job']] = -1
				crew[c['job']] = {}
			ncrew[c['job']] += 1

			if 'release_date' in c:
				rd =  c['release_date']
			else:
				rd = ''
			job = {	'id': c['id'],
									'title': c['title'],
									'release_date': rd,
									'poster_path': c['poster_path']
							}
			crew[c['job']][ncrew[c['job']]] = job
	else:
		cast = {}
		crew = {}
	return {'cast': cast, 'crew': crew}

#region IT
def getUpcoming():
	url = baseUrl + '/movie/upcoming?api_key=' + apikey + '&language=en-US&page=1&region=IT'
	json_r = requests.get(url).json()
	return json_r['results']


def getNowPlaying():
	url = baseUrl + '/movie/now_playing?api_key=' + apikey + '&language=en-US&page=1&region=IT'
	json_r = requests.get(url).json()
	return json_r['results']

def getPersonByID(personID):
	url = 'https://api.themoviedb.org/3/person/'+ str(personID) +'?api_key=' + apikey
	# json_r = {}
	# if(personID != None):
	# 	json_r = requests.get(url).json()
	# return json_r
	#tmdb = getToken()
	#person = Person()

	data = requests.get(url).json()
	if not 'success' in data or data['success'] != False:
		person_info = {}
		person_info['id'] = data['id']
		person_info['birthday'] = data['birthday']
		person_info['deathday'] = data['deathday']
		person_info['name'] = data['name']
		person_info['gender'] = data['gender']
		person_info['biography'] = data['biography']
		person_info['place_of_birth'] = data['place_of_birth']
		person_info['profile_path'] = data['profile_path']
		person_info['popularity'] = data['popularity']
		person_info['adult'] = data['adult']
		person_info['imdb_id'] = data['imdb_id']
		person_info['homepage'] = data['homepage']
	else:
		person_info = {}
	return person_info

def searchByYear(title, year):
	url = 'https://api.themoviedb.org/3/search/movie?api_key=' + apikey +'&query=' + title + '&year=' + year
	json_r = requests.get(url).json()
	results = json_r['results']
	if json_r['total_results'] == 0:
		results = getMovieByName(title,1)[0]
	#pprint.pprint(results)
	return results[0]

def letterboxdImport(file):
	ids = []
	firstline = True
	i = 1
	with codecs.open(file, "r", encoding='utf-8', errors='ignore') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			if firstline:
				firstline = False
				continue
			#res.append(row[1])
			#movie = getMovieByImdbID(row[1])
			#res.append(movie)
			title = row[1]
			year = row[2]
			date = row[0]
			rating=row[4]
			movie = searchByYear(title,year)[0]
			print("{}: {}".format(i,movie['id']))
			addToDB(movie['id'])
			i=i+1
	return ids

def addToDB(movieID):
	addRe = 'INSERT OR IGNORE INTO movtra_movie VALUES (%d,"%s", %d, %d, "%s", "%s", "%s", "%s","%s",%d,"%s","%s","%s",%d,%d,"%s","%s","%s","%s",%f,%d,"%s")'
	movie = getMovieByID(movieID)
	#pprint.pprint(movie)
	conn = sqlite3.connect('/home/theloca95/UMT/db.sqlite3')
	conn.execute(addRe % (int(movie['id']),
                          movie['adult'],
                          0,
                          int(movie['budget']),
                          movie['homepage'],
                          movie['imdb_id'],
                          movie['original_language'],
                          movie['original_title'],
                          movie['overview'],
                          int(movie['popularity']),
                          movie['backdrop_path'],
                          movie['poster_path'],
                          movie['release_date'],
                          int(movie['revenue']),
                          int(movie['runtime']),
                          movie['status'],
                          movie['tagline'],
                          movie['title'],
                          movie['video'],
                          float(movie['vote_average']),
                          int(movie['vote_count']),
                          "11-12-2012")
                )
	conn.commit()
	return None

#if __name__ == "__main__":
	#getMovieByName('psycho')
	#getUpcoming()
	#getMovieByID(550)
	#getPersonByID(7467)
	#letterboxdImport("/home/theloca95/letterbox/diary.csv")
	#addToDB(21)
	#print('done')
	#m = getMovieByID('399407')
	#getMovieByName('Report')
	#pprint.pprint(m)
	#pprint.pprint(importImdb('./WATCHLIST.csv'))
	#importImdb('./WATCHLIST.csv')
	#cast = getFilmography(4429)
	#pprint.pprint(cast)
	#a = searchByYear('The King of Comedy','1983')
	#pprint.pprint(a)
	path = Path(join(dirname(__file__)))
	dotensv_path = join(path.parent.parent, '.env')