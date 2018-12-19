from tmdbv3api import TMDb, Movie, Person
import tmdbsimple as tmdb
import requests
import json
import pprint
import csv
import codecs
import tempfile
import urllib.request
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
apikey = os.getenv('APIKEY')
def getToken():
	tmdb = TMDb()
	tmdb.api_key = apikey
	return tmdb

def getMovieByID(tmdbID):
	url = 'https://api.themoviedb.org/3/movie/'+ str(tmdbID) +'?api_key=' + apikey + "&append_to_response=credits"
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

def getMovieByName(movieName):
	url = 'https://api.themoviedb.org/3/search/movie?api_key=' + apikey + '&query=' + movieName 
	#+'&year=1967'
	json_r = requests.get(url).json()
	results = json_r['results']
	#pprint.pprint(results)
	return results

def getMovieByImdbID(imdbID):
	url = 'https://api.themoviedb.org/3/find/'+ imdbID +'?api_key='+ apikey +'&external_source=imdb_id'
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

def getPersonID(name):
	url = 'http://api.tmdb.org/3/search/person?api_key=88b9df7c1eb6689e78cf9b5ec24a0c1e&query=quentin%20tarantino'
	return True

def getFilmography(personID):
	url = 'https://api.themoviedb.org/3/person/'+ personID +'/movie_credits?api_key=' + apikey + '&language=en-US'
	#directing
	#acting
	#writing
	return True

def getUpcoming():
	getToken()
	movie = Movie()
	return movie.upcoming()


def getNowPlaying():
	getToken()
	movie = Movie()
	return movie.now_playing()

def getPersonByID(personID):
	# url = 'https://api.themoviedb.org/3/person/'+ str(personID) +'?api_key=' + apikey
	# json_r = {}
	# if(personID != None):
	# 	json_r = requests.get(url).json()
	# return json_r
	tmdb = getToken()
	person = Person()
	data = person.details(personID)
	person_info = {}
	person_info['id'] = data.id
	person_info['birthday'] = data.birthday
	person_info['deathday'] = data.deathday
	person_info['name'] = data.name
	person_info['gender'] = data.gender
	person_info['biography'] = data.biography
	person_info['place_of_birth'] = data.place_of_birth
	person_info['profile_path'] = data.profile_path
	person_info['popularity'] = data.popularity
	person_info['adult'] = data.adult
	person_info['imdb_id'] = data.imdb_id
	person_info['homepage'] = data.homepage
	
	return person_info

if __name__ == "__main__":
	#getMovieByName('psycho')
	#getUpcoming()
	#getMovieByID(550)
	getPersonByID(7467)
	print('done')
	#m = getMovieByID('399407')
	#getMovieByName('Report')
	#pprint.pprint(m)
	#pprint.pprint(importImdb('./WATCHLIST.csv'))
	#importImdb('./WATCHLIST.csv')