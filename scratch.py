import requests
import os
from pprint import pprint

QUERY_MOVIE = "strange"
TMDB_API_KEY = os.environ.get('TMDB_Apikey')
TMDB_ACCESS_TOKEN =os.environ.get('TMDB_Access_Token')
poster = None




search_endpoint = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=en-US&query={QUERY_MOVIE}&page=1&include_adult=false'

video_key = None
search_id = None
trailer = f'https://www.youtube.com/watch?v={video_key}'
videos = "&append_to_response=videos,images"

response = requests.get(url=search_endpoint)
search_data = response.json()['results']

for data in search_data:
    search_id = data['id']
    search_title = data['title']
    search_date = data['release_date']


m_response = requests.get(url=f'https://api.themoviedb.org/3/movie/{search_id}?api_key={TMDB_API_KEY}&append_to_response=videos')
movie_data = m_response.json()
poster = movie_data['poster_path']
title = movie_data['title']
description = movie_data['overview']
ranking = movie_data['vote_average']
year = movie_data['release_date'].split('-')[0]
# video_key = movie_data['videos']['results'][0]['key']
poster_endpoint = f'https://image.tmdb.org/t/p/original{poster}'
pprint(movie_data)