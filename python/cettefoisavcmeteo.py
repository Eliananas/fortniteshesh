# import necessary modules
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, jsonify
import requests
import random
import datetime

# initialize Flask app
app = Flask(__name__)

# set the name of the session cookie
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

# set a random secret key to sign the cookie
app.secret_key = 'YOUR_SECRET_KEY'

# set the key for the token info in the session dictionary
TOKEN_INFO = 'token_info'

# route to handle logging in
@app.route('/')
def login():
    # create a SpotifyOAuth instance and get the authorization URL
    auth_url = create_spotify_oauth().get_authorize_url()
    # redirect the user to the authorization URL
    return redirect(auth_url)

# route to handle the redirect URI after authorization
@app.route('/redirect')
def redirect_page():
    # clear the session
    session.clear()
    # get the authorization code from the request parameters
    code = request.args.get('code')
    # exchange the authorization code for an access token and refresh token
    token_info = create_spotify_oauth().get_access_token(code)
    # save the token info in the session
    session[TOKEN_INFO] = token_info
    # redirect the user to the save_discover_weekly route
    return redirect(url_for('get_top_tracks',_external=True))

@app.route('/get_top_tracks')
def get_top_tracks():
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_top_tracks(limit=20, offset=0, time_range='short_term')  # Modifier la limite à 20
    track_ids = [track['id'] for track in results['items']]
    selected_track_ids = random.sample(track_ids, 5)  # Sélectionner aléatoirement 5 IDs
    session['track_ids'] = selected_track_ids  # Stocker les IDs sélectionnés dans la session
    return redirect(url_for('getlocation', _external=True))

@app.route('/getlocation', methods=['GET', 'POST'])
def getlocation():
    return '''
        <form action="/getmeteo" method="post">
            City: <input type="text" name="city">
            <input type="submit" value="Get Weather">
        </form>
    '''

@app.route('/getmeteo', methods=['GET', 'POST'])  # Allow both GET and POST
def getmeteo():
    city = request.form.get('city') if request.method == 'POST' else request.args.get('city')
    session['city'] = city
    if not city:
        return "City not specified", 400
    
    # Remplacez {API key} par votre clé d'API personnelle d'OpenWeatherMap
    api_key = "6c9e30b56a098814c0810b64050066c1"
    session ["api_key"] = api_key
    # Construire l'URL pour la requête à l'API de géolocalisation
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    response = requests.get(geo_url).json()
    if response and isinstance(response, list) and len(response) > 0:
    # Access the first item in the list
        city_data = response[0]
        lat = city_data.get('lat')
        lon = city_data.get('lon')
        if lat and lon:
            session['lat'] = lat
            session['lon'] = lon
            return redirect(url_for('getweather', _external=True))
        else:
            return "No data found for the specified city 1", 404
    else:
        return "No data found for the specified city 2", 404
    
@app.route('/getweather')
def getweather():
    lat = session['lat']
    lon = session['lon']
    part = 'daily, minutely, hourly, alerts'
    meteo_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=hourly,daily,minutely,alerts&appid={session['api_key']}&units=metric"
    response = requests.get(meteo_url)  # Make a GET request to the API
    if response.status_code == 200:
        meteo_data = response.json()  # Parse the JSON response
        # Assuming 'current' weather data is what you're after, adjust as necessary
        current_weather = meteo_data.get('current', {})
        temp = current_weather.get('temp')
        clouds = current_weather.get('clouds')
        ressenti = current_weather.get('feels_like')
        if 'weather' in current_weather and len(current_weather['weather']) > 0:
            weather_id = current_weather['weather'][0].get('id')
            weather_main = current_weather['weather'][0].get('main')
            weather_description = current_weather['weather'][0].get('description')
            if temp and clouds and ressenti and weather_id and weather_main and weather_description:
                session['temp'] = temp
                session['clouds'] = clouds
                session['ressenti'] = ressenti
                session['weather_id'] = weather_id
                session['weather_main'] = weather_main
                session['weather_description'] = weather_description
                return redirect(url_for('choosemoodweather', _external=True))
    return "No data found for the specified city 3", 404

@app.route('/choosemoodweather')
def choosemoodweather():
    if session['temp'] > 20 and session['clouds'] < 50 and session['ressenti'] > 20 :
                mood = "heureux"
                session['mood'] = mood
                return redirect(url_for('choosemood', _external=True))
    elif session['temp'] < 20 and session['clouds'] < 50 and session['ressenti'] > 20 :
                mood = "heureux"
                session['mood'] = mood
                return redirect(url_for('choosemood', _external=True))
    elif session['temp'] > 20 and session['clouds'] > 50 and session['ressenti'] > 20 :
                mood = "heureux"
                session['mood'] = mood
                return redirect(url_for('choosemood', _external=True))
    elif session['temp'] > 20 and session['clouds'] > 50 and session['ressenti'] < 20 :
                mood = "triste"
                session['mood'] = mood
                return redirect(url_for('choosemood', _external=True))
    elif session['temp'] < 20 and session['clouds'] < 50 and session['ressenti'] < 20 :
                mood = "triste"
                session['mood'] = mood
                return redirect(url_for('choosemood', _external=True))
    elif session['temp'] < 20 and session['clouds'] > 50 and session['ressenti'] < 20 :
                mood = "triste"
                session['mood'] = mood
                return redirect(url_for('choosemood', _external=True))
    elif session['temp'] < 20 and session['clouds'] > 70 and session['ressenti'] < 16 :
                mood = "Dépressif"
                session['mood'] = mood
                return redirect(url_for('choosemood', _external=True))
    elif session['temp'] > 20 and session['clouds'] < 25 and session['ressenti'] > 20 :
                mood = "énergique"
                session['mood'] = mood
                return redirect(url_for('choosemood', _external=True))
    elif session['temp'] and session['clouds'] and session['ressenti']:
                return 'Les éléments sont existants mais Mood non reconnu', 400
    return "Mood non reconnu", 400
    


genres_h= []

genres_t= []

genres_e= []

genres_d= []

mood_genre_map = {
    'heureux': genres_h,
    'triste': genres_t,
    'énergique': genres_e,
    'Dépressif': genres_d
}

@app.route('/choosemood', methods=['GET', 'POST'])
def choosemood():
    if session['mood'] == "triste":
                attribute = {
                    'target_acousticness':1,
                    'target_danceability':0,
                    'target_energy':0.3,
                    'target_instrumentalness':0.5,
                    'target_loudness': -15,
                    'target_popularity': 'pop',
                    'target_speechiness':0,
                    'target_valence':0
                    }
                session['target_acousticness'] = attribute['target_acousticness']
                session['target_danceability'] = attribute['target_danceability']
                session['target_energy'] = attribute['target_energy']
                session['target_instrumentalness'] = attribute['target_instrumentalness']
                session['target_loudness'] = attribute['target_loudness']
                session['target_popularity'] = attribute['target_popularity']
                session['target_speechiness'] = attribute['target_speechiness']
                session['target_valence'] = attribute['target_valence']
                return redirect(url_for('createreccs', _external=True))
    elif session['mood'] == "heureux":
                attribute = {
                    'target_acousticness':0.3,
                    'target_danceability':0.75,
                    'target_energy':0.3,
                    'target_instrumentalness':0,
                    'target_loudness': -45,
                    'target_popularity': 'pop',
                    'target_speechiness':0.5,
                    'target_valence':1
                    }
                session['target_acousticness'] = attribute['target_acousticness']
                session['target_danceability'] = attribute['target_danceability']
                session['target_energy'] = attribute['target_energy']
                session['target_instrumentalness'] = attribute['target_instrumentalness']
                session['target_loudness'] = attribute['target_loudness']
                session['target_popularity'] = attribute['target_popularity']
                session['target_speechiness'] = attribute['target_speechiness']
                session['target_valence'] = attribute['target_valence']
                return redirect(url_for('createreccs', _external=True))
    elif session['mood'] == "énergique":
                attribute = {
                    'target_acousticness':0,
                    'target_danceability':0.3,
                    'target_energy':1,
                    'target_instrumentalness':0,
                    'target_loudness': -60,
                    'target_popularity': 'pop',
                    'target_speechiness':0.75,
                    'target_valence':0.75
                    }
                session['target_acousticness'] = attribute['target_acousticness']
                session['target_danceability'] = attribute['target_danceability']
                session['target_energy'] = attribute['target_energy']
                session['target_instrumentalness'] = attribute['target_instrumentalness']
                session['target_loudness'] = attribute['target_loudness']
                session['target_popularity'] = attribute['target_popularity']
                session['target_speechiness'] = attribute['target_speechiness']
                session['target_valence'] = attribute['target_valence']
                return redirect(url_for('createreccs', _external=True))
    elif session['mood'] == "Dépressif":
                attribute = {
                    'target_acousticness':0.5,
                    'target_danceability':1,
                    'target_energy':0,
                    'target_instrumentalness':1,
                    'target_loudness': 0,
                    'target_popularity': 'pop',
                    'target_speechiness':1,
                    'target_valence':0.3
                    }
                session['target_acousticness'] = attribute['target_acousticness']
                session['target_danceability'] = attribute['target_danceability']
                session['target_energy'] = attribute['target_energy']
                session['target_instrumentalness'] = attribute['target_instrumentalness']
                session['target_loudness'] = attribute['target_loudness']
                session['target_popularity'] = attribute['target_popularity']
                session['target_speechiness'] = attribute['target_speechiness']
                session['target_valence'] = attribute['target_valence']
                return redirect(url_for('createreccs', _external=True))
    else:
            return 'Mood non reconnu', 400


@app.route('/createreccs')
def createreccs():
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info['access_token'])
    target_acousticness = session['target_acousticness']
    target_danceability = session['target_danceability']
    target_energy = session['target_energy']
    target_instrumentalness =session['target_instrumentalness'] 
    target_loudness = session['target_loudness']
    target_popularity = session['target_popularity']
    target_speechiness = session['target_speechiness']
    target_valence = session['target_valence']
    reccs_results = sp.recommendations(seed_artists=None, seed_tracks=session['track_ids'], limit=50, country=None, target_acousticness=target_acousticness, target_danceability=target_danceability, target_energy=target_energy, target_instrumentalness=target_instrumentalness, target_loudness=target_loudness, target_speechiness=target_speechiness, target_valence=target_valence)
    recc_ids = [recc['id'] for recc in reccs_results['tracks']]
    session['recc_ids'] = recc_ids
    return redirect(url_for('createplaylist', _external=True))


@app.route('/createplaylist')
def createplaylist():
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user=user_id, name='Playlist mood: ' + session['mood'], public=False, collaborative=False, description='Playlist créée le ' + datetime.date.today().strftime('%Y-%m-%d') + ' avec ' + str(session['clouds']) + '% de nuages ' + 'La température ressentie est de ' + str(session['ressenti']) + ' degrés. PLAYLIST GENERATED BY METEOFY-SQW1RRL')
    recc_track_ids = session.get('recc_ids', [])  # Récupérer les IDs des morceaux de la session
    if recc_track_ids:
        sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=recc_track_ids)
    return 'Actuellement, il fait ' + str(session['temp']) + ' degrés à ' + str(session['city']) + '\n' + "Il y'as des " + str(session['weather_main']) + ' avec ' + str(session['clouds']) + '% de nuages.\n La température ressentie est de ' + str(session['ressenti']) + ' degrés Celsius.\nLe mood de playlist qui vous est donc conseillé est un mood plutôt ' + str(session['mood']) + '.\n Bref, entre temps, votre playlist a été créée avec succès général!'


# function to get the token info from the session
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        # if the token info is not found, redirect the user to the login route
        redirect(url_for('login', _external=False))
    
    # check if the token is expired and refresh it if necessary
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = '36f87bd49fc947e88df5309b9d507ab2',
        client_secret = '7bbb6144833a4745abd0a89886806a9e',
        redirect_uri = url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private user-top-read'
    )

app.run(debug=True)