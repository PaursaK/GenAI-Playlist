from flask import Flask, render_template, redirect, request, url_for, session
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import secrets
import requests
load_dotenv()




# Initialize the Flask app
app = Flask(__name__)

# Set the secret key to secure session cookies
app.secret_key = os.getenv('SECRET_KEY')

# Initialize OAuth
oauth = OAuth(app)

# Spotify OAuth Setup
spotify = oauth.register(
    'spotify',
    client_id=os.environ.get('SPOTIFY_CLIENT_ID'),
    client_secret=os.environ.get('SPOTIFY_CLIENT_SECRET'),
    authorize_url='https://accounts.spotify.com/authorize',
    access_token_url='https://accounts.spotify.com/api/token',
    client_kwargs={'scope': 'user-library-read playlist-modify-public playlist-modify-private user-read-email user-read-private'},
)


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login/spotify')
def spotify_login():
    # Generate a random state value for security
    session['oauth_state'] = secrets.token_hex(16)
    
    # Redirect to Spotify's authorization page
    return spotify.authorize_redirect(
        redirect_uri=url_for('spotify_callback', _external=True),
        state=session['oauth_state']
    )

@app.route('/callback/spotify')
def spotify_callback():
    # Verify the state parameter
    if session.get('oauth_state') != request.args.get('state'):
        return 'State verification failed', 400
    
    try:
        # Get the access token
        token = spotify.authorize_access_token()
        
        # Store the token in session
        session['spotify_token'] = token
        
        # Redirect to home page after successful authentication
        return redirect(url_for('home'))
    except Exception as e:
        return f'Error during authentication: {str(e)}', 400

@app.route('/home')
def home():
    if 'spotify_token' not in session:
        return redirect(url_for('login'))
    
    # Get user profile information from Spotify
    token = session['spotify_token']
    headers = {
        'Authorization': f"Bearer {token['access_token']}"
    }
    
    try:
        # Fetch user profile
        profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        profile_data = profile_response.json()
        
        # Fetch user's playlists
        playlists_response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)
        playlists_data = playlists_response.json()
        
        return render_template('home.html', 
                             user=profile_data,
                             playlists=playlists_data['items'])
    except Exception as e:
        return f"Error fetching user data: {str(e)}", 400

@app.route('/logout')
def logout():
    # Clear the session data
    session.pop('spotify_token', None)
    session.pop('oauth_state', None)
    
    # Redirect to the login page after logout
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)


