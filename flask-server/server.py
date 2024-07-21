import js2py
import requests
import base64
from flask import Flask, request, redirect, jsonify, make_response
import os
import hashlib
import random
import string
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="36f87bd49fc947e88df5309b9d507ab2",
                                               client_secret="7bbb6144833a4745abd0a89886806a9e",
                                               redirect_uri="http://127.0.0.1:8888/login",
                                               scope="user-read-playback-state playlist-read-private playlist-modify-public user-top-read"))


client_id = '36f87bd49fc947e88df5309b9d507ab2'  # your clientId
client_secret = '7bbb6144833a4745abd0a89886806a9e'  # Your secret
redirect_uri = 'http://localhost:8888/callback'  # Your redirect uri

app = Flask(__name__)
state_key = 'spotify_auth_state'

def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

@app.route('/login')
def login():
    state = generate_random_string(16)
    response = make_response(redirect(
        'https://accounts.spotify.com/authorize?' +
        f'response_type=code&client_id={client_id}&scope=user-read-private user-read-email&redirect_uri={redirect_uri}&state={state}'
    ))
    response.set_cookie(state_key, state)
    return response

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = request.cookies.get(state_key)

    if state is None or state != stored_state:
        return redirect('/#' + 'error=state_mismatch')
    else:
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            data={
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            },
            headers={
                'Authorization': 'Basic ' + base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode(),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        if response.status_code == 200:
            body = response.json()
            access_token = body.get('access_token')
            refresh_token = body.get('refresh_token')

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            user_info_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
            print(user_info_response.json())

            return redirect('/#' + f'access_token={access_token}&refresh_token={refresh_token}')
        else:
            return redirect('/#' + 'error=invalid_token')

@app.route('/refresh_token')
def refresh_token():
    refresh_token = request.args.get('refresh_token')
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        },
        headers={
            'Authorization': 'Basic ' + base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode(),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )

    if response.status_code == 200:
        body = response.json()
        return jsonify({
            'access_token': body.get('access_token'),
            'refresh_token': body.get('refresh_token')
        })
    else:
        return jsonify({'error': 'failed_to_refresh_token'}), response.status_code

if __name__ == '__main__':
    app.run(port=8888)

# Spotify Algorithme de recommandation de playlist personnalisée en Python
def limit_seeds(track_ids, max_seeds=5):
    """
    Limite le nombre de seeds à un maximum spécifié (par défaut 5).

    :param track_ids: Liste des identifiants de pistes (ou autres seeds).
    :param max_seeds: Nombre maximum de seeds à retourner.
    :return: Sous-liste des identifiants limitée à max_seeds éléments.
    """
    # Retourne jusqu'à max_seeds éléments de la liste
    return track_ids[:max_seeds]

def get_top_track_ids():
    """
    Collecte les identifiants uniques des top tracks de l'utilisateur sur différentes périodes.
    """
    # Exemple de récupération des identifiants de pistes (remplacez ceci par votre propre logique)
    top_track_ids = ["id1", "id2", "id3", "id4", "id5", "id6", "id7"]  # Supposons que ceci soit le résultat

    # Limiter les seeds à 5
    limited_seeds = limit_seeds(top_track_ids)

    # Utiliser limited_seeds pour la requête de recommandation
    # Exemple: sp.recommendations(seed_tracks=limited_seeds)
    return limited_seeds

def get_recommended_track_ids_for_mood(seed_tracks, genres_str):
    url = "https://api.spotify.com/v1/recommendations"
    params = {
        'limit': 20,
        'seed_genres': genres_str,
        'seed_tracks': ','.join(seed_tracks[:5])  # Ensure only up to 5 seed tracks are used
    }
    response = requests.get(url, params=params, headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"})
    if response.status_code == 200:
        return [track['id'] for track in response.json()['tracks']]
    else:
        print(f"Erreur lors de la récupération des recommandations : http status: {response.status_code}, code:-1 - {response.url}:\n {response.reason}")
        return []
    
    
def create_playlist_with_recommended_tracks(sp, recommended_track_ids, mood):
    if not recommended_track_ids:
        print("Aucune piste recommandée à ajouter à la playlist.")
        return

    # Ensure recommended_track_ids are in the correct format
    uris = ["spotify:track:" + track_id for track_id in recommended_track_ids if not track_id.startswith("spotify:track:")]

    # Ensure there are URIs to add
    if not uris:
        print("Erreur : Aucun URI valide fourni pour la création de la playlist.")
        return

    playlist_id = 'VotrePlaylistID'  # Replace with your actual playlist ID
    try:
        sp.playlist_add_items(playlist_id=playlist_id, items=uris)
        print(f"Playlist pour l'humeur '{mood}' mise à jour avec succès.")
    except spotipy.exceptions.SpotifyException as e:
        print(f"Erreur lors de la mise à jour de la playlist : {e}")

def create_mood_playlists(top_track_ids):
    """
    Demande à l'utilisateur de choisir un mood et crée une playlist correspondante
    basée sur les recommandations et les genres musicaux pertinents.
    """
    moods = {
        "HEUREUX": ["pop", "dance", "kpop"],
        "TRISTE": ["acoustic", "piano"],
        "EXCITÉ": ["rock", "dance", "electronic"]
    }

    # Demander à l'utilisateur de choisir un mood
    print("Choisissez un mood: h, t, e")
    user_choice = input("Votre choix: ").upper()

    # Vérifier que le choix est valide
    while user_choice not in moods:
        print("Choix invalide. Veuillez choisir entre: HEUREUX, TRISTE, EXCITÉ")
        user_choice = input("Votre choix: ").upper()

    # Créer la playlist pour le mood choisi
    genres = moods[user_choice]
    # Filter out any empty strings from the genres list before joining
    # Ensure genres list does not contain empty strings or null values
    genres = list(filter(None, genres))  # Filter out falsy values: '', None, etc.
    genres_str = ','.join(genres)

    # Debugging: Print genres list after filtering
    print("Filtered genres:", genres_str)

    recommended_track_ids = get_recommended_track_ids_for_mood(top_track_ids[:5], genres_str)
    create_playlist_with_recommended_tracks(sp, recommended_track_ids, user_choice)
    # Exécution
    top_track_ids = get_top_track_ids()
    create_mood_playlists(top_track_ids)



# Exécution
top_track_ids = get_top_track_ids()
create_mood_playlists(top_track_ids)