# import necessary modules
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect

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
    results = sp.current_user_top_tracks(limit=4, offset=0, time_range='short_term')
    track_ids = [track['id'] for track in results['items']]
    session['track_ids'] = track_ids  # Stocker les IDs des morceaux dans la session
    return redirect(url_for('choosemood', _external=True))

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
    if request.method == 'POST':
        mood = request.form['mood']
        session['mood'] = mood
        genre = mood_genre_map.get(mood)
        session['genre'] = genre
        if mood:
            if mood == "triste":
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
            elif mood == "heureux":
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
            elif mood == "énergique":
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
            elif mood == "Dépressif":
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
    # Retourner un formulaire pour choisir le mood si la méthode est GET
    return '''
        <form method="post">
            Mood: <input type="text" name="mood">
            <input type="submit" value="Créer Playlist">
        </form>
    '''


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
    reccs_results = sp.recommendations(seed_artists=None, seed_genres=session['genre'], seed_tracks=session['track_ids'], limit=20, country=None, target_acousticness=target_acousticness, target_danceability=target_danceability, target_energy=target_energy, target_instrumentalness=target_instrumentalness, target_loudness=target_loudness, target_speechiness=target_speechiness, target_valence=target_valence)
    recc_ids = [recc['id'] for recc in reccs_results['tracks']]
    session['recc_ids'] = recc_ids
    return redirect(url_for('createplaylist', _external=True))


@app.route('/createplaylist')
def createplaylist():
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user=user_id, name='Playlist pour une personne '+ session['mood'] , public=False, collaborative=False, description='GENERATED BY SQW1RRL')
    recc_track_ids = session.get('recc_ids', [])  # Récupérer les IDs des morceaux de la session
    if recc_track_ids:
        sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=recc_track_ids)
    return 'Playlist created'


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