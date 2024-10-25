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

#Route et fonctions qui vont nous permettre de prendre les 20 morceaux les plus écoutés sur court terme (1 semaine ou 2)
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
    <html>
        <head>
            <title>Entrez votre ville</title>
            <style>
                /* Style global pour la page */
                body {
                    background-color: #191414;
                    color: #FFFFFF;
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    overflow: hidden;
                }
                
                /* Barre de navigation */
                .navbar {
                    background-color: #2e2e33;
                    width: 100%;
                    padding: 15px 0;
                    position: fixed;
                    top: 0;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                    z-index: 1000;
                }
                .navbar img {
                    height: 50px;
                    margin-left: 20px;
                }
                .navbar h1 {
                    color: #1DB954;
                    margin-right: 20px;
                    font-size: 24px;
                    font-weight: bold;
                    text-align: center;
                    animation: fadeIn 1.5s ease-in-out;
                }
                
                /* Conteneur du formulaire */
                .form-container {
                    background-color: #282828;
                    padding: 40px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
                    animation: slideUp 1.5s ease-in-out;
                }

                .form-container h2 {
                    color: #1DB954;
                    margin-bottom: 20px;
                    font-size: 22px;
                }

                .form-container input[type="text"] {
                    width: 100%;
                    padding: 15px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: 2px solid #1DB954;
                    margin-bottom: 20px;
                    outline: none;
                    transition: all 0.3s ease;
                }
                
                .form-container input[type="text"]:focus {
                    border-color: #02b44b;
                    box-shadow: 0 0 10px rgba(29, 185, 84, 0.5);
                }

                .form-container button {
                    background-color: #1DB954;
                    color: #FFFFFF;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 30px;
                    font-size: 18px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                    box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
                }

                .form-container button:hover {
                    background-color: #02b44b;
                    box-shadow: 0 6px 15px rgba(29, 185, 84, 0.5);
                }

                /* Animations */
                @keyframes slideUp {
                    0% {
                        transform: translateY(50%);
                        opacity: 0;
                    }
                    100% {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }

                @keyframes fadeIn {
                    0% {
                        opacity: 0;
                    }
                    100% {
                        opacity: 1;
                    }
                }

                /* Mobile responsiveness */
                @media (max-width: 768px) {
                    .form-container {
                        padding: 20px;
                        width: 90%;
                    }
                    .navbar img {
                        height: 40px;
                    }
                    .navbar h1 {
                        font-size: 20px;
                    }
                }
            </style>
        </head>
        <body>
            <!-- Barre de navigation -->
            <div class="navbar">
                <a href="/"><img src="https://s1.gifyu.com/images/SOkIP.png" alt="meteorifylogo"></a>
                <h1>Bienvenue sur Meteorify</h1>
            </div>

            <!-- Contenu principal -->
            <div class="form-container">
                <h2>Veuillez insérer la ville où vous vous situez.</h2>
                <form action="/getmeteo" method="post">
                    <input type="text" id="city" name="city" placeholder="Ex: Paris" required>
                    <br>
                    <button type="submit">Obtenir la météo</button>
                </form>
            </div>
        </body>
    </html>
    '''


@app.route('/getmeteo', methods=['GET', 'POST'])  # Allow both GET and POST
def getmeteo():
    city = request.form.get('city') if request.method == 'POST' else request.args.get('city')
    session['city'] = city
    if not city:
                return '''
    <html>
        <head>
            <title>Entrez votre ville</title>
            <style>
                /* Style pour la barre de navigation */
                .navbar {
                    background-color: #5b5c66;
                    position: fixed;
                    top: 0;
                    width: 100%;
                    height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: flex-start;
                    box-shadow: 0 4px 2px -2px gray;
                    z-index: 1000;
                }
                /* Style pour l'image dans la barre de navigation */
                .navbar img {
                    height: 40px;
                }
                /* Style pour le contenu principal */
                body {
                    background-color: #191414;
                    color: #FFFFFF;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin: 0;
                    padding: 0;
                    padding-top: 80px; /* Pour ne pas que le contenu soit masqué par la barre de navigation */
                }
                /* Style du formulaire */
                .form-container {
                    margin-top: 50px;
                }
                input[type="text"] {
                    padding: 10px;
                    font-size: 16px;
                    border-radius: 5px;
                    border: 1px solid #1DB954;
                    margin: 10px;
                }
                button {
                    background-color: #1DB954;
                    color: #FFFFFF;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <!-- Barre de navigation -->
            <div class="navbar">
                <a href="https://ibb.co/qrpydwW" style="margin-left: 20px;"><img src="https://i.ibb.co/qrpydwW/meteorifylogo.png" alt="meteorifylogo" border="0"></a>   
                <h1 style="color: #02b44b; margin-left:auto; margin-right:auto;">Bienvenue sur meteorify !</h1>       
            </div>

            <!-- Contenu principal -->
            <div class="form-container">
                <text style="color: #1DB954;"><strong><i>Plongez dans une expérience musicale personnalisée qui s'adapte à chaque moment de votre journée.</i></strong></text>
                <h2 style="color: #1DB954;">Veuillez insérer la ville où vous vous situez.</h2>
                <form action="/getmeteo" method="post">
                    <input type="text" id="city" name="city" placeholder="Ex: Paris">
                    <br>
                    <button type="submit">Obtenir la météo</button>
                </form>
                <h2 style="color: #ff2727;">Veuilez insérer une ville!</h2>
            </div>
        </body>
    </html>
    '''

    
    api_key = "6c9e30b56a098814c0810b64050066c1"  
    session["api_key"] = api_key

    # Construire l'URL pour la requête à l'API de géolocalisation
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    
    response = requests.get(geo_url).json()
    print(f"Geolocation API response: {response}")  # Pour voir la réponse de l'API dans la console s'il y as des bugs/soucis

    if response and isinstance(response, list) and len(response) > 0:
        # Accéder au premier élément de la réponse
        city_data = response[0]
        lat = city_data.get('lat')
        lon = city_data.get('lon')
        if lat and lon:
            session['lat'] = lat
            session['lon'] = lon
            return redirect(url_for('getweather', _external=True))
        else:
                    return '''
    <html>
        <head>
            <title>Entrez votre ville</title>
            <style>
                /* Style pour la barre de navigation */
                .navbar {
                    background-color: #5b5c66;
                    position: fixed;
                    top: 0;
                    width: 100%;
                    height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: flex-start;
                    box-shadow: 0 4px 2px -2px gray;
                    z-index: 1000;
                }
                /* Style pour l'image dans la barre de navigation */
                .navbar img {
                    height: 40px;
                }
                /* Style pour le contenu principal */
                body {
                    background-color: #191414;
                    color: #FFFFFF;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin: 0;
                    padding: 0;
                    padding-top: 80px; /* Pour ne pas que le contenu soit masqué par la barre de navigation */
                }
                /* Style du formulaire */
                .form-container {
                    margin-top: 50px;
                }
                input[type="text"] {
                    padding: 10px;
                    font-size: 16px;
                    border-radius: 5px;
                    border: 1px solid #1DB954;
                    margin: 10px;
                }
                button {
                    background-color: #1DB954;
                    color: #FFFFFF;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <!-- Barre de navigation -->
            <div class="navbar">
                <a href="https://ibb.co/qrpydwW" style="margin-left: 20px;"><img src="https://i.ibb.co/qrpydwW/meteorifylogo.png" alt="meteorifylogo" border="0"></a>   
                <h1 style="color: #02b44b; margin-left:auto; margin-right:auto;">Bienvenue sur meteorify !</h1>       
            </div>

            <!-- Contenu principal -->
            <div class="form-container">
                <text style="color: #1DB954;"><strong><i>Plongez dans une expérience musicale personnalisée qui s'adapte à chaque moment de votre journée.</i></strong></text>
                <h2 style="color: #1DB954;">Veuillez insérer la ville où vous vous situez.</h2>
                <form action="/getmeteo" method="post">
                    <input type="text" id="city" name="city" placeholder="Ex: Paris">
                    <br>
                    <button type="submit">Obtenir la météo</button>
                </form>
                <h2 style="color: #ff2727;">Cette ville n'est pas valide...</h2>
            </div>
        </body>
    </html>
    '''

    else:
        return '''
    <html>
        <head>
            <title>Entrez votre ville</title>
            <style>
                /* Style pour la barre de navigation */
                .navbar {
                    background-color: #5b5c66;
                    position: fixed;
                    top: 0;
                    width: 100%;
                    height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: flex-start;
                    box-shadow: 0 4px 2px -2px gray;
                    z-index: 1000;
                }
                /* Style pour l'image dans la barre de navigation */
                .navbar img {
                    height: 40px;
                }
                /* Style pour le contenu principal */
                body {
                    background-color: #191414;
                    color: #FFFFFF;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin: 0;
                    padding: 0;
                    padding-top: 80px; /* Pour ne pas que le contenu soit masqué par la barre de navigation */
                }
                /* Style du formulaire */
                .form-container {
                    margin-top: 50px;
                }
                input[type="text"] {
                    padding: 10px;
                    font-size: 16px;
                    border-radius: 5px;
                    border: 1px solid #1DB954;
                    margin: 10px;
                }
                button {
                    background-color: #1DB954;
                    color: #FFFFFF;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <!-- Barre de navigation -->
            <div class="navbar">
                <a href="https://ibb.co/qrpydwW" style="margin-left: 20px;"><img src="https://i.ibb.co/qrpydwW/meteorifylogo.png" alt="meteorifylogo" border="0"></a>   
                <h1 style="color: #02b44b; margin-left:auto; margin-right:auto;">Bienvenue sur meteorify !</h1>       
            </div>

            <!-- Contenu principal -->
            <div class="form-container">
                <text style="color: #1DB954;"><strong><i>Plongez dans une expérience musicale personnalisée qui s'adapte à chaque moment de votre journée.</i></strong></text>
                <h2 style="color: #1DB954;">Veuillez insérer la ville où vous vous situez.</h2>
                <form action="/getmeteo" method="post">
                    <input type="text" id="city" name="city" placeholder="Ex: Paris">
                    <br>
                    <button type="submit">Obtenir la météo</button>
                </form>
                <h2 style="color: #ff2727;">Cette ville n'est pas valide...</h2>
            </div>
        </body>
    </html>
    '''

#Route d'accueil apres authentification où l'utilisateur va mettre sa location où une ville aléatoire   
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
            return '''
    <html>
        <head>
            <title>Entrez votre ville</title>
            <style>
                /* Style pour la barre de navigation */
                .navbar {
                    background-color: #5b5c66;
                    position: fixed;
                    top: 0;
                    width: 100%;
                    height: 60px;
                    display: flex;
                    align-items: center;
                    justify-content: flex-start;
                    box-shadow: 0 4px 2px -2px gray;
                    z-index: 1000;
                }
                /* Style pour l'image dans la barre de navigation */
                .navbar img {
                    height: 40px;
                }
                /* Style pour le contenu principal */
                body {
                    background-color: #191414;
                    color: #FFFFFF;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin: 0;
                    padding: 0;
                    padding-top: 80px; /* Pour ne pas que le contenu soit masqué par la barre de navigation */
                }
                /* Style du formulaire */
                .form-container {
                    margin-top: 50px;
                }
                input[type="text"] {
                    padding: 10px;
                    font-size: 16px;
                    border-radius: 5px;
                    border: 1px solid #1DB954;
                    margin: 10px;
                }
                button {
                    background-color: #1DB954;
                    color: #FFFFFF;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <!-- Barre de navigation -->
            <div class="navbar">
                <a href="https://ibb.co/qrpydwW" style="margin-left: 20px;"><img src="https://i.ibb.co/qrpydwW/meteorifylogo.png" alt="meteorifylogo" border="0"></a>   
                <h1 style="color: #02b44b; margin-left:auto; margin-right:auto;">Bienvenue sur meteorify !</h1>       
            </div>

            <!-- Contenu principal -->
            <div class="form-container">
                <text style="color: #1DB954;"><strong><i>Plongez dans une expérience musicale personnalisée qui s'adapte à chaque moment de votre journée.</i></strong></text>
                <h2 style="color: #1DB954;">Veuillez insérer la ville où vous vous situez.</h2>
                <form action="/getmeteo" method="post">
                    <input type="text" id="city" name="city" placeholder="Ex: Paris">
                    <br>
                    <button type="submit">Obtenir la météo</button>
                </form>
                <h2style="color:red;">Cette ville n'est pas valide...</h2>
            </div>
        </body>
    </html>
    '''


@app.route('/choosemoodweather')
def choosemoodweather():
    if session['temp'] > 20 and session['clouds'] < 50 and session['clouds'] > 25 and session['ressenti'] > 20 :
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
                    'target_energy':0.1,
                    'target_instrumentalness':0.5,
                    'target_loudness': -15,
                    'target_popularity': 50,
                    'target_speechiness':0,
                    'target_valence':0,
                    'min_tempo':80,
                    'max_tempo':120,
                    'target_tempo': 100
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
                    'target_popularity': 75,
                    'target_speechiness':0.5,
                    'target_valence':1,
                    'min_tempo':90,
                    'max_tempo':140,
                    'target_tempo': 125
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
                    'target_popularity': 85,
                    'target_speechiness':0.75,
                    'target_valence':0.75,
                    'min_tempo':120,
                    'max_tempo':180,
                    'target_tempo': 140
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
                    'target_acousticness':1,
                    'target_danceability':0,
                    'target_energy':0,
                    'target_instrumentalness':1,
                    'target_loudness': 0,
                    'target_popularity': 10,
                    'target_speechiness':1,
                    'target_valence':0.3,
                    'min_tempo':60,
                    'max_tempo':110,
                    'target_tempo': 90
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
    
    # Récupérer l'ID utilisateur Spotify
    user_id = sp.me()['id']
    
    # Créer une nouvelle playlist avec le mood et la météo
    playlist = sp.user_playlist_create(
        user=user_id, 
        name='Playlist mood: ' + session['mood'], 
        public=False, 
        collaborative=False, 
        description=f'Playlist créée le {datetime.date.today().strftime("%Y-%m-%d")} avec {session["clouds"]}% de nuages. '
                    f'La température ressentie est de {session["ressenti"]} degrés. '
                    f'PLAYLIST GENERATED BY METEOFY-SQW1RRL'
    )
    
    # Ajouter les morceaux recommandés à la playlist
    recc_track_ids = session.get('recc_ids', [])
    if recc_track_ids:
        sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=recc_track_ids)
    
    # Lien vers la playlist Spotify
    playlist_url = playlist['external_urls']['spotify']
    
    # Dictionnaire pour les GIFs en fonction de l'émotion
    gifs = {
        'heureux': 'https://s1.gifyu.com/images/SOkm5.gif',  # Remplacer par un vrai lien vers un GIF "heureux"
        'triste': 'https://s1.gifyu.com/images/SOkkK.gif',  # Remplacer par un vrai lien vers un GIF "triste"
        'énergique': 'https://s11.gifyu.com/images/SOkmJ.gif',  # Remplacer par un vrai lien vers un GIF "énergique"
        'Dépressif': 'https://s1.gifyu.com/images/SOkki.gif'   # Remplacer par un vrai lien vers un GIF "dépressif"
    }
    
    # Récupérer le lien GIF correspondant à l'émotion actuelle
    mood_gif = gifs.get(session['mood'])

    # Retourner un message de succès à l'utilisateur avec du style et un GIF en arrière-plan
    return f'''
    <body style="background-image: url('{mood_gif}'); background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;">
    <div style="background-color: rgba(0, 0, 0, 1); color: #1DB954; font-family: 'Arial', sans-serif; padding: 30px; border-radius: 10px; text-align: center; margin: 0 auto; width: 40%; position: relative; top: 10%; transform: translateY(-50%);">
    <a href="/" style="text-decoration: none;">
            <img src="https://s1.gifyu.com/images/SOkIP.png" alt="Logo" style="max-width: 40%; cursor: pointer;">
        </a>    
    </div>
    <div style="background-color: rgba(0, 0, 0, 1); color: #1DB954; font-family: 'Arial', sans-serif; padding: 20px; border-radius: 10px; text-align: center; margin: 0 auto; width: 60%; position: relative; top: 40%; transform: translateY(-50%);">
        <h2 style="color: #1DB954;">Playlist créée avec succès !</h2>
        <p>Actuellement, il fait <strong>{session["temp"]} degrés</strong> à <strong>{session["city"]}</strong>.</p>
        <p>Il y a <strong>{session["clouds"]}%</strong> de nuages.</p>
        <p>La température ressentie est de <strong>{session["ressenti"]} degrés Celsius</strong>.</p>
        <p>Le mood de playlist conseillé est un mood plutôt <strong>{session["mood"]}</strong>.</p>
        <p>Votre playlist a été créée avec succès !</p>
        
        <!-- Bouton pour ouvrir la playlist sur Spotify -->
        <a href="{playlist_url}" target="_blank" style="display: inline-block; background-color: #1DB954; color: white; padding: 10px 20px; text-decoration: none; border-radius: 50px; font-weight: bold; margin-top: 20px;">
            Ouvrir sur Spotify
        </a>
    </div>
    
    </body>
    '''



#RECUPERE GITHUB

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