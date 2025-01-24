import os
from flask import Flask, request, redirect, session, url_for
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

#load environment variables from .env file
load_dotenv()

app = Flask(__name__)

#Set a secret key for flask sessions
app.secret_key = os.getenv("FLASK_SECRET_KEY", "someFallbackKey")

#Spotipy configuration from environment variables
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# Scopes define which permissions you need from the user
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

@app.route('/')
def index():
    if 'token_info' in session:
        return "Already logged in. Go to /playlists or /currently_playing."
    else:
        return redirect(url_for('login'))
    
@app.route('/login')
#Initiates the spotify login process
def login():
    sp_oath = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                           client_secret=SPOTIPY_CLIENT_SECRET,
                           redirect_uri=SPOTIPY_REDIRECT_URI,
                           scope=SCOPE)
    auth_url = sp_oath.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
#Exchanges auth code for an access token and stores in session
def callback():
    sp_oath = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                           client_secret=SPOTIPY_CLIENT_SECRET,
                           redirect_uri=SPOTIPY_REDIRECT_URI,
                           scope=SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oath.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('index'))

def get_spotify_client():
    """
    Helper function to refresh the token when needed 
    and return a Spotipy client.
    """
    token_info = session.get('token_info', None)
    if not token_info:
        return None

    # Check if token is expired and refresh if necessary
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                            client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI,
                            scope=SCOPE)

    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    return spotipy.Spotify(auth=token_info['access_token'])


@app.route('/playlists')
def get_playlists():
    """
    Example endpoint to fetch and display the user's playlists.
    """
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for('login'))

    results = sp.current_user_playlists(limit=10)
    playlist_names = [playlist['name'] for playlist in results['items']]
    return f"Your playlists: {', '.join(playlist_names)}"


@app.route('/currently_playing')
def currently_playing():
    """
    Example endpoint to show the currently playing track.
    """
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for('login'))
    
    current_track_info = sp.current_user_playing_track()
    if current_track_info is None or not current_track_info.get('item'):
        return "No track is currently playing."
    
    track_name = current_track_info['item']['name']
    artist_name = current_track_info['item']['artists'][0]['name']
    return f"Currently playing: {track_name} by {artist_name}"


@app.route('/play_pause_toggle')
def play_pause_toggle():
    """
    Example endpoint to either pause or resume playback depending on the current state.
    """
    sp = get_spotify_client()
    if not sp:
        return redirect(url_for('login'))

    # Check the current track
    current_track_info = sp.current_user_playing_track()
    if current_track_info and current_track_info.get('is_playing'):
        sp.pause_playback()
        return "Playback paused."
    else:
        sp.start_playback()
        return "Playback started/resumed."


if __name__ == "__main__":
    app.run(debug=True)