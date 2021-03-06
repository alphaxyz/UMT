from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import Movie, List, isIn, Genres, isGenre, WorkedAsCast, WorkedAsCrew, Company, Produce, Country, ProductionCountry, Language, SpokenLanguage, LogEntry
from .utils import tmdb_api_wrap
import pprint
import csv
import codecs
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core import serializers
from django.db import IntegrityError
import json
from itertools import islice
from datetime import datetime
from datetime import timedelta
import random
import pycountry

# Create your views here.

def index(request):
    latest_movies_list = Movie.objects.raw("""  select movtra_movie.*, movtra_logentry.* 
                                                from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id 
                                                where movtra_logentry.date is not null 
                                                order by date desc;
                                            """)
    context = {'latest_movies_list': latest_movies_list, 'all': False}
    return render(request, 'movtra/index.html', context)

def all(request):
    latest_movies_list = Movie.objects.order_by('-last_updated')[:24]
    context = {'latest_movies_list': latest_movies_list, 'all': True}
    return render(request, 'movtra/index.html', context)

def upcoming(request):
    upcoming = tmdb_api_wrap.getUpcoming()
    context =  {'results': upcoming,
                 'type': 1 # type 1 upcoming/nowplaying
                }
    return render(request, 'movtra/results.html', context)

def nowplaying(request):
    nowplaying = tmdb_api_wrap.getNowPlaying()
    context = {'results': nowplaying,
                'type': 1 # type 1 upcoming/nowplaying
                }
    return render(request, 'movtra/results.html', context)

# Return the serialization of a Movie entry
def serialize_movie(movie_entry):
    movie = {}
    for attr,k in movie_entry.__dict__.items():
        movie[attr] = k
    return movie

# Movie detail view
def detail(request, tmdbID):
        local = False # db presence flag
        try:
            # Check if the movie is in the db
            movie = Movie.objects.get(id=tmdbID)
            movie_serialized = serialize_movie(movie)
            local = True
        except Movie.DoesNotExist:
            movie = None
        if movie is None: # If not present in the db, get the information
            movie = tmdb_api_wrap.getMovieByID(tmdbID)
            genres=movie['genres']
            directors = {}
            dID=0
            for p in movie['credits']['crew']:
               if p['job'] == 'Director':
                    directors[dID] = {'name': p['name'], 'id': p['id']}
                    dID+=1
    
            g = []
            for gen in genres:
                g.append(gen['name'])
            return render(request, 'movtra/detail.html', {'movie': movie, 'genres': genres, 'directors': directors, 'local': local})
        else: # Otherwise look if it's present in any list
            isin = isIn.objects.filter(movie=movie).order_by('list')
            lists = {}
            lID=0
            for l in isin:
                lists[lID] = {'id': l.list.id,
                          'name': l.list.name}
                lID+=1

            # Uniform the genres and directors
            isgenre = isGenre.objects.filter(movie=movie)
            genres = []
            for g in isgenre:
                genres.append(g.genre.name)
            mov = tmdb_api_wrap.getMovieByID(tmdbID)
            genres=mov['genres']
            
            directors = {}
            dID=0
            for p in mov['credits']['crew']:
               if p['job'] == 'Director':
                    directors[dID] = {'name': p['name'], 'id': p['id']}
                    dID+=1

            # Get diary entries
            diary_entries = LogEntry.objects.filter(movie=movie)
            diary = {}
            eID = 0
            for e in diary_entries:
                diary[eID] = {'id': e.id,
                              'date': e.date,
                              'rating': e.rating,
                              'review': e.review}
                eID+=1
            return render(request, 'movtra/detail.html', {'movie': movie, 'lists': lists, 'genres': genres, 'directors' : directors, 'diary': diary, 'local': local})

# Log Movie function (refactor)
def logMovie(request):
    if request.method == 'POST':	
        date = request.POST.get('bday')
        tmdbID = request.POST.get('tmdbID')
        rating = request.POST.get('rating')
        review = ""
        review = request.POST.get('review')
        data = {'tmdbID': tmdbID , 'date': date, 'rating': rating, 'review': review}
        
        try:
            mov = Movie.objects.get(id=tmdbID)
        except Movie.DoesNotExist:
            mov = None
        if mov is None:
            addMovie(tmdbID)
        LogEntry.addLogEntry(data)
    return redirect(request.META['HTTP_REFERER'])

def search(request):
    query = ''
    if request.method == 'POST':
            query = request.POST.get('searchTitle')
    return redirect("/results/"+query+"/1")

def results(request, query, page):
    if page != '':
        page = page
    else:
        page = 1
    if request.method == 'POST':
            movieName = request.POST.get('searchTitle')
            if movieName == '':
                movieName = query
    else:
        movieName = query
    query = movieName

    if ' ' in movieName:
        movieName = movieName.replace(' ','+')
    results = tmdb_api_wrap.getMovieByName(movieName,page)
    total_pages = results[1]

    if page == total_pages:
        isNext = False
    else:
        isNext = True
    
    if page == 1:
        isBack = False
    else:
        isBack = True
    context = {'query': movieName ,'next_page': int(page)+1, 'isNext': isNext, 'back_page': int(page)-1 ,'isBack': isBack, 'page': page, 'results': results[0] , 'total_pages': total_pages, 'type': 0} #type 0 search
    return render(request, 'movtra/results.html', context)



# General purpose function to add a movie given its id to the dB
def addMovie(tmdbID):
    try:
        mov = Movie.objects.get(pk=tmdbID)
    except Movie.DoesNotExist:
        movie_data = tmdb_api_wrap.getMovieByID(tmdbID)
        try:
            Movie.addShow(movie_data)
            mov = Movie.objects.get(pk=tmdbID)
            
            for genre in movie_data['genres']:
                try:
                    genreID = Genres.objects.get(pk=genre['id'])
                    genreID = genre['id']
                except Genres.DoesNotExist:
                    genreID = Genres.addGenre(genre)
                isGenre.addGenreToMovie(tmdbID,genreID)
            
            for company in movie_data['production_companies']:
                try:
                    companyID = Company.objects.get(pk=company['id'])
                    companyID = company['id']
                except Company.DoesNotExist:
                    companyID = Company.addNewCompany(company)
                Produce.addProdutionCompany(tmdbID, companyID)

            for country in movie_data['production_countries']:
                try:
                    countryID = Country.objects.get(pk=country['iso_3166_1'])
                    countryID = country['iso_3166_1']
                except Country.DoesNotExist:
                    countryID = Country.addCountry(country)
                ProductionCountry.addProductionCountry(tmdbID, countryID)
            
            for language in movie_data['spoken_languages']:
                try:
                    languageID = Language.objects.get(pk=language['iso_639_1'])
                    languageID = language['iso_639_1']
                except Language.DoesNotExist:
                    languageID = Language.addLanguage(language)
                SpokenLanguage.addSpokenLanguage(tmdbID, languageID)
            
            # cast & crew
            credits = movie_data['credits']

            cast_objs = []
            batch_size = 0
            for personData in credits['cast']:
                try:
                    WorkedAsCast.objects.get(movie = mov, 
                                        cast_id = int(personData['cast_id']),
                                        character = personData['character'],
                                        credit_id = personData['credit_id'],
                                        gender = int(personData['gender']),
                                        person_id = str(personData['id']),        
                                        name = personData['name'],       
                                        order = int(personData['order']),
                                        profile_path = personData['profile_path'])
                except WorkedAsCast.DoesNotExist:
                    el = WorkedAsCast(movie = mov,
                                        cast_id = int(personData['cast_id']),
                                        character = personData['character'],
                                        credit_id = personData['credit_id'],
                                        gender = int(personData['gender']),
                                        person_id = str(personData['id']),        
                                        name = personData['name'],       
                                        order = int(personData['order']),
                                        profile_path = personData['profile_path'])
                    cast_objs.append(el)
                    batch_size +=1
                        
            # Manage the mySQL 999 varaibles limit
            while batch_size > 0:
                batch = list(islice(cast_objs, batch_size))
                
                if batch_size> 99:
                    WorkedAsCast.objects.bulk_create(batch[:100], batch_size)
                    batch_size -= 100
                else:
                    WorkedAsCast.objects.bulk_create(batch, batch_size)
                    batch_size = 0

            
            crew_objs = []
            batch_size = 0
            for personData in credits['crew']:
                try:
                    WorkedAsCrew.objects.get(movie = tmdbID, 
                                        credit_id = personData['credit_id'],
                                        department = personData['department'],
                                        gender = int(personData['gender']),
                                        person_id = str(personData['id']), 
                                        job = personData['job'],       
                                        name = personData['name'],       
                                        profile_path = personData['profile_path'])
                except WorkedAsCrew.DoesNotExist:
                    el = WorkedAsCrew(movie = mov,
                                        credit_id = personData['credit_id'],
                                        department = personData['department'],
                                        gender = int(personData['gender']),
                                        person_id = str(personData['id']), 
                                        job = personData['job'],       
                                        name = personData['name'],       
                                        profile_path = personData['profile_path'])
                    crew_objs.append(el)
                    batch_size +=1 
            # Manage the mySQL 999 varaibles limit
            while batch_size > 0:
                batch = list(islice(crew_objs, batch_size))
                
                if batch_size> 99:
                    WorkedAsCrew.objects.bulk_create(batch[:100], batch_size)
                    batch_size -= 100
                else:
                    WorkedAsCrew.objects.bulk_create(batch, batch_size)
                    batch_size = 0
                      
        except Exception as e:
            print("Something is wrong")
            print(e)
            isGenre.objects.filter(movie=tmdbID).delete()
            Produce.objects.filter(movie=tmdbID).delete()
            WorkedAsCast.objects.filter(movie=tmdbID).delete()
            WorkedAsCrew.objects.filter(movie=tmdbID).delete()
            Movie.objects.filter(id=tmdbID).delete()

# Update information for existing movies
def updateData(request, tmdbID):
    if request.method == 'POST':
        try:
            mov = Movie.objects.get(id=tmdbID)
        except IntegrityError:
            print('Movie not present in the db')
        movie = tmdb_api_wrap.getMovieByID(tmdbID)
        Movie.addShow(movie)
        for genre in movie['genres']:
            try:
                genreID = Genres.objects.get(pk=genre['id'])
                genreID = genre['id']
            except Genres.DoesNotExist:
                genreID = Genres.addGenre(genre)
            isGenre.addGenreToMovie(tmdbID,genreID)
        for company in movie['production_companies']:
            try:
                companyID = Company.objects.get(pk=company['id'])
                companyID = company['id']
            except Company.DoesNotExist:
                companyID = Company.addNewCompany(company)
            Produce.addProdutionCompany(tmdbID, companyID)
        for country in movie['production_countries']:
            try:
                countryID = Country.objects.get(pk=country['iso_3166_1'])
                countryID = country['iso_3166_1']
            except Country.DoesNotExist:
                countryID = Country.addCountry(country)
            ProductionCountry.addProductionCountry(tmdbID, countryID)
        for language in movie['spoken_languages']:
            try:
                languageID = Language.objects.get(pk=language['iso_639_1'])
                languageID = language['iso_639_1']
            except Language.DoesNotExist:
                languageID = Language.addLanguage(language)
            SpokenLanguage.addSpokenLanguage(tmdbID, languageID)

        # cast & crew
        credits = movie['credits']

        cast_objs = []
        batch_size = 0
        
        for personData in credits['cast']:
            try:
                WorkedAsCast.objects.get(movie = mov, 
                                        cast_id = int(personData['cast_id']),
                                        character = personData['character'],
                                        credit_id = personData['credit_id'],
                                        gender = int(personData['gender']),
                                        person_id = str(personData['id']),        
                                        name = personData['name'],       
                                        order = int(personData['order']),
                                        profile_path = personData['profile_path'])
            except WorkedAsCast.DoesNotExist:
                el = WorkedAsCast(movie = mov,
                                    cast_id = int(personData['cast_id']),
                                    character = personData['character'],
                                    credit_id = personData['credit_id'],
                                    gender = int(personData['gender']),
                                    person_id = str(personData['id']),        
                                    name = personData['name'],       
                                    order = int(personData['order']),
                                    profile_path = personData['profile_path'])
                cast_objs.append(el)
                batch_size +=1

            # Manage the mySQL 999 varaibles limit
        while batch_size > 0:
            batch = list(islice(cast_objs, batch_size))
            
            if batch_size> 99:
                WorkedAsCast.objects.bulk_create(batch[:100], batch_size)
                batch_size -= 100
            else:
                WorkedAsCast.objects.bulk_create(batch, batch_size)
                batch_size = 0

        crew_objs = []
        batch_size = 0
        for personData in credits['crew']:
            try:
                WorkedAsCrew.objects.get(movie = mov, 
                                    credit_id = personData['credit_id'],
                                        department = personData['department'],
                                        gender = int(personData['gender']),
                                        person_id = str(personData['id']), 
                                        job = personData['job'],       
                                        name = personData['name'],       
                                        profile_path = personData['profile_path'])
            except WorkedAsCrew.DoesNotExist:
                el = WorkedAsCrew(movie = mov,
                                    credit_id = personData['credit_id'],
                                    department = personData['department'],
                                    gender = int(personData['gender']),
                                    person_id = str(personData['id']), 
                                    job = personData['job'],       
                                    name = personData['name'],       
                                    profile_path = personData['profile_path'])
                crew_objs.append(el)
                batch_size +=1 

        # Manage the mySQL 999 varaibles limit
        while batch_size > 0:
            batch = list(islice(cast_objs, batch_size))
            
            if batch_size> 99:
                WorkedAsCast.objects.bulk_create(batch[:100], batch_size)
                batch_size -= 100
            else:
                WorkedAsCast.objects.bulk_create(batch, batch_size)
                batch_size = 0
        return HttpResponseRedirect('/movie/%d' % tmdbID)
    return HttpResponseRedirect('/')

#List view (lists)
def lists(request):
    context = {}
    list = List.objects.all()
    context['list'] = list
    return render(request, 'movtra/lists.html', context)

#List view (list of movies)
def listDetail(request, id):
    lst = List.objects.get(id=id)
    movies = isIn.objects.filter(list=lst).order_by('id')

    # Counts the number of watched movies in the list
    if not movies.exists:
        watched_count = 0
    else:
        watched_list = Movie.objects.raw('select distinct movtra_movie.* , movtra_logentry.id as log_id from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id join movtra_isin on movtra_isin.movie_id=movtra_movie.id where movtra_isin.list_id=' + str(id) + ' group by movtra_movie.id;')
        watched_count =0
        for _ in watched_list:
            watched_count+=1

    context = {'movies': movies, 'list': lst ,'total':len(movies), 'watched': watched_count , 'logentry': list(watched_list)}
    return render(request, 'movtra/listDetail.html', context)

#Import button in list (WIP)
def importList(request, id):
    """movies = tmdb_api_wrap.importImdb('./movtra/utils/10.csv')
    i=0
    for movie in movies:
        tmdbID = tmdb_api_wrap.getMovieByImdbID(movie)['id']
        addMovie(tmdbID)
        i=i+1
        try:
            isIn.addShow(tmdbID,id)
        except IntegrityError:
            print(str(i) + ': ' + str(tmdbID) + ' duplicate')
        print(str(i) + ': ' + str(tmdbID) + ' added')
    return HttpResponseRedirect('../')"""
    #letterboxdImport("/home/theloca95/letterbox/diary.csv")
    letterboxdImport("C:/Users/thelo/Desktop/diary.csv",id)
    return HttpResponseRedirect('../')

#Imports movies from a letterboxd file
def letterboxdImport(file, list_id):
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
            date = row[-1]
            rating = row[4]
            if rating == '':
                rating = None

            movie = tmdb_api_wrap.searchByYear(title,year)
            if 'total_results' not in movie:
                movie_id = movie['id']
                print("{}: {}".format(i,movie_id))
                addMovie(movie_id)
                isIn.addShow(movie_id,list_id)
                data = {'tmdbID': movie_id, 'date': date , 'rating': rating, 'review': ''}
                LogEntry.addLogEntry(data)
            i=i+1
    return ids

#Create a new list
def newList(request):
    context = {}
    if request.method == 'POST':
        listTitle = request.POST.get('listTitle')
        list = List.objects.all()
        List.addShow(listTitle)

    context['list'] = list
    return render(request, 'movtra/lists.html', context)

def addToList(request, id):
    context = {}
    movieName = request.POST.get('listTitle')
    if ' ' in movieName:
        movieName = movieName.replace(' ','+')
    results = tmdb_api_wrap.getMovieByName(movieName,1) #return (results, number of results)
    context = {'results': results[0] , 'total_pages': results[1], 'list_id': id, 'type': 2} # type 2 list
    return render(request, 'movtra/results.html', context)

def addMovieToList(request, id):
    context = {}
    if request.method == 'POST':
        listID = int(request.POST.get('listid'))
        mov = addMovie(id)
        try:
            isIn.addShow(id,listID)
        except IntegrityError:
            print('duplicate')
        return HttpResponseRedirect('/lists/%d' % listID)
    return HttpResponseRedirect('/')

def editList(request, id):
    lst = List.objects.get(id=id)

    movies = isIn.objects.filter(list=lst).order_by('id')
    movs = {}
    movieIDs = []
    wmovieIDs = []
    i=0
    for m in movies:
        #movieIDs.append(m.movie.id)
        movs[i] = {'id': m.movie.id, 'title': m.movie.title, 'year': str(m.movie.release_date)[:4]}
        i+=1

    if not movies.exists:
        #watched_count = len(isIn.objects.filter(list=list).filter(movie__status_watched=True))
        watched_count = 0
    else:
        #watched_count = Movie.objects.raw('select distinct movtra_movie.* from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id join movtra_isin on movtra_isin.movie_id=movtra_movie.id where movtra_isin.list_id='+str(id) +';')
        watched_count = Movie.objects.raw('select distinct movtra_movie.* , movtra_logentry.id as log_id from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id join movtra_isin on movtra_isin.movie_id=movtra_movie.id where movtra_isin.list_id=' + str(id) + ' group by movtra_movie.id;')
        #watched_count = Movie.objects.raw('select movtra_movie.*, movtra_logentry.date from movtra_movie join movtra_logentry on movtra_logentry.movie_id=movtra_movie.id order by date desc;')
        w=0
        for wc in watched_count:
            wmovieIDs.append(wc.id)
            w+=1

    #print(watched_count)
    #context = {'movies': movieIDs, 'list': id ,'total':len(movieIDs), 'watched': w, 'logentry': list(watched_count)}
    context = {'movies': movs, 'list': lst ,'total':i, 'watched': w, 'logentry': wmovieIDs}
    return render(request, 'movtra/editList.html', context)
    #return JsonResponse(context)
    #return HttpResponse(json.dumps(context))

def editLists(request):
    context = {}
    list = List.objects.all()
    context['list'] = list
    return render(request, 'movtra/listsEdit.html', context)


def removeListsGET(request):
    pprint.pprint(request)
    if request.method == 'GET':
        listID = request.GET['list_id']
        print(listID)
        List.objects.filter(id=listID).delete()
        isIn.objects.filter(list_id=listID).delete()
        return HttpResponse("Success!")
    else:
        print("Something is wrong")
        return HttpResponse("Request method is not a GET")

def removeMovieFromListGET(request):
    if request.method == 'GET':
        movieID = request.GET['movie_id']
        listID = request.GET['list_id']
        isIn.objects.filter(list_id=listID).filter(movie_id=movieID).delete()
        return HttpResponse("Success!")
    else:
        print("Something is wrong")
        return HttpResponse("Request method is not a GET")

def removeDiaryEntry(request, tmdbID, diaryID):
    LogEntry.objects.filter(id=diaryID).delete()
    return redirect(request.META['HTTP_REFERER'])

#TODO
def editReview(request, tmdbID):
    movie = get_object_or_404(Movie, pk=tmdbID)
    context = {'movie': movie}
    if request.method == 'POST':
        print(request.POST.get('text'))
    return render(request, 'movtra/editReview.html', context)

def saveReview(request, tmdbID):
    if request.method == 'POST':
        data = request.POST.get('text')
    movie = get_object_or_404(Movie, pk=tmdbID)
    Movie.addReview(movie,data)
    return HttpResponseRedirect('./')

def personDetail(request, tmdbID):
    personData = tmdb_api_wrap.getPersonByID(tmdbID)
    filmography = tmdb_api_wrap.getFilmography(tmdbID)

    pwatched_query = """select  distinct movie_id, *
                        from	(select distinct le.*
                            from movtra_logentry as le
                            join movtra_workedascast as wct on le.movie_id=wct.movie_id
                            where wct.person_id ='{0}'
                            group by le.movie_id
                            union all
                            select distinct le.*
                            from movtra_logentry as le
                            join movtra_workedascrew as wcw on le.movie_id=wcw.movie_id
                            where wcw.person_id = '{0}'
                            group by le.movie_id)
                        """.format(tmdbID)

    pwatched_raw = LogEntry.objects.raw(pwatched_query)
    watched = []
    for w in pwatched_raw:
        watched.append(int(w.movie_id))

    # horrible way to get sorted filmography
    #credit_list = dict(filmography['crew'].items())
    #credit_list['Actor'] = dict(filmography['cast'].items())
    credit_list = {'Actor' : dict(filmography['cast'].items()) }
    credit_list.update(dict(filmography['crew'].items()))
    s = {}
    for j, q in credit_list.items():       
        res = {}
        for k, v in q.items():
            res[v['id']] = v['release_date']
        rd = sorted(res.values())
        m = 0
        y=0

        # put blanks at the end of the array
        while y<len(rd) and rd[m] == '':
            n = 0
            while n<len(rd)-1:
                rd[n] = rd[n+1]
                n +=1
            rd[len(rd)-1] = ''
            y +=1

        ps = {}

        for k, v in q.items():
            i = rd.index(v['release_date'])
            ps[i] = v
        sps = dict(sorted(ps.items()))
        s[j] = sps

    
    credits_slug = {k.replace(' ', '_'): v for k, v in s.items()}

    context = {'person': personData, 'crew': filmography['crew'], 'credits_slug': credits_slug, 'watched':watched}
    return render(request, 'movtra/personDetail.html', context)

# Statistics
def getLastDay(any_day):
    """Finds the last day of the month in the form yyyy-mm-dd
    :param any_day: a day of the month of which we want to find the last day
    :return: the last day of the month
    """
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return (next_month - timedelta(days=next_month.day)).strftime("%Y-%m-%d")

def stats(request):
    years_query = """select *
                    from movtra_logentry as le 
                    """
    years_raw = LogEntry.objects.raw(years_query)
    years = []
    for log in years_raw:
        year = log.date.strftime("%Y")
        if year not in years:
            years.append(year)

    print(years)
    # On this date
    today = datetime.today().strftime("%m-%d")
    month = datetime.today().strftime("%B")
    on_this_day_query = """  select movtra_movie.* , movtra_logentry.date
                                            from movtra_logentry
                                            left join movtra_movie on movtra_logentry.movie_id = movtra_movie.id
                                            where date like '____-{}'
                                            """.format(today)
    on_this_day = Movie.objects.raw(on_this_day_query)
    
    # Genre (month) TODO:add month selection
    first_day = "2017-00-01" #debug
    last_day = "2017-12-31" #debug
    #first_day = datetime.today().replace(day=1).strftime("%Y-%m-%d")  
    #last_day = getLastDay(datetime.today())

    genre_query = """ select *, count() as count
                        from movtra_logentry as le 
                        left join movtra_isgenre ig on le.movie_id=ig.movie_id
                        left join movtra_genres ge on ge.id=ig.genre_id
                        where  le.date >= '{}' and le.date <= '{}'
                        group by ig.genre_id
                    """.format(first_day, last_day)

    genre_raw = isGenre.objects.raw(genre_query)
    genre = {}
    g_tot = 0
    for g in genre_raw:
        genre[g.name] = g.count
        g_tot += g.count

    
    ad = 0
    g_col = {}
    for g in genre_raw:
        genre[g.name] = round(g.count * 100 / g_tot, 2)
        g_col[g.name] = "#%06x" % random.randint(0, 0xFFFFFF) # random hex
        ad += g.count * 100 / g_tot

    # Most viewed directors
    mwd_query = """select *, count() as count
                    from movtra_logentry as le 
                    left join movtra_workedascrew wc on le.movie_id=wc.movie_id
                    where  le.date >= '{}' and le.date <= '{}' and wc.job='Director'
                    group by wc.person_id
                    order by count desc
                    limit 5
                """.format(first_day, last_day)
    mwd_raw = WorkedAsCrew.objects.raw(mwd_query)

    # Most viewed actors
    mwa_query = """select *, count() as count
                    from movtra_logentry as le 
                    left join movtra_workedascast wc on le.movie_id=wc.movie_id
                    where  le.date >= '{}' and le.date <= '{}'
                    group by name
                    order by count desc
                    limit 5
                """.format(first_day, last_day)
    mwa_raw = WorkedAsCast.objects.raw(mwa_query)

    # Production Companies
    pdc_query ="""select *, count() as count
                from movtra_logentry as le 
                left join movtra_productioncountry pc on le.movie_id=pc.movie_id
                where  le.date >= '{}' and le.date <= '{}' and pc.movie_id is not NULL
                group by pc.country_id
                """.format(first_day, last_day)

    pdc_raw = LogEntry.objects.raw(pdc_query)
    countries = {}
    for country in pycountry.countries:
        countries[country.alpha_2] = country.alpha_3

    pdc_dict = {}
    for pc in pdc_raw:
        country_alpha2 = countries[pc.country_id]
        pdc_dict[country_alpha2] = pc.count

    pprint.pprint(pdc_dict)
    context = {'on_this_day': on_this_day, 'month': month, 'today': today, 'genre': genre, 'g_col': g_col, 'mwd': mwd_raw, 'mwa': mwa_raw, 'years': years, 'pdc': pdc_dict }
    return render(request, 'movtra/stats.html', context)

#TODO cache manager
# if (\wsdasd.jpg) exists use it else download and use it
# genres page

#select movtra_movie.id
#from movtra_isgenre, movtra_movie
#where movtra_isgenre.genre_id=18 and movtra_isgenre.movie_id=movtra_movie.id;

#log movie when adding

#https://stackoverflow.com/questions/34774138/reload-table-data-in-django-without-refreshing-the-page/34775420
