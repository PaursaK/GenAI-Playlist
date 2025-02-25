from flask import Flask, render_template, redirect, request, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import secrets
import requests
import json
import openai
import random
import sys
load_dotenv()




# Initialize the Flask app
app = Flask(__name__)

# Set up your OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

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
    client_kwargs={'scope': 'streaming user-library-read playlist-modify-public playlist-modify-private user-read-email user-read-private user-read-playback-state user-modify-playback-state app-remote-control'
},
)


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login/spotify')
def spotify_login():
    # Generate a random state value for security
    session['oauth_state'] = secrets.token_hex(16)
    
    # Redirect to Spotify's authorization page with updated scope
    return spotify.authorize_redirect(
        redirect_uri=url_for('spotify_callback', _external=True),
        state=session['oauth_state'],
        scope='streaming user-library-read playlist-modify-public playlist-modify-private user-read-email user-read-private user-read-playback-state user-modify-playback-state app-remote-control'
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
    
    token = session['spotify_token']
    headers = {
        'Authorization': f"Bearer {token['access_token']}"
    }
    
    try:
        # Fetch user profile
        profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        profile_data = profile_response.json()
        
        # Check if the response is valid
        if 'error' in profile_data:
            return f"Error fetching user data: {profile_data['error']['message']}", 400

        return render_template('home.html', 
                            user=profile_data,
                            playlists=[],
                            spotify_token=token['access_token'])  # Check if token is passed correctly
    except Exception as e:
        return f"Error fetching user data: {str(e)}", 400

@app.route('/generate', methods=['POST'])
def generate_playlist():
    try:
        data = request.get_json()
        user_input = data.get('playlist_prompt')
        
        if not user_input or user_input.strip() == "":
            return jsonify({"error": "Empty input received"}), 400
        
        genres = get_music_genres(user_input)
        
        if not genres:
            return jsonify({"error": "No genres found from input."}), 400
        
        playlists = []
        for genre in genres:
            token = session.get('spotify_token')
            if not token:
                return jsonify({"error": "Spotify token missing."}), 400

            headers = {
                'Authorization': f"Bearer {token['access_token']}"
            }

            search_url = "https://api.spotify.com/v1/search"
            params = {
                "q": f"genre:{genre}",
                "type": "track",
                "limit": 20,
            }

            search_response = requests.get(search_url, headers=headers, params=params)

            if search_response.status_code == 200:
                data = search_response.json()
                tracks = data.get("tracks", {}).get("items", [])

                if not tracks:
                    return jsonify({"error": "No tracks found for this genre."}), 400

                songs = [{
                    "name": t["name"],
                    "artist": t["artists"][0]["name"],
                    "uri": t["uri"],
                    "images": t["album"]["images"] if "album" in t else []  # Access album images here
                } for t in tracks]

                # Check if there's at least one song to access its image
                if songs and songs[0]["images"]:
                    playlist_image = songs[0]["images"][0]["url"]  # Use the first image of the first song
                else:
                    playlist_image = "default_image_url_here"  # Fallback if no image is found

                playlist = {
                    "name": f"Playlist for {genre}",
                    "description": f"Curated playlist for the {genre} genre.",
                    "external_urls": {"spotify": "https://open.spotify.com"},
                    "images": [{"url": playlist_image}],
                    "tracks": {"items": songs}
                }

                playlists.append(playlist)
            else:
                return jsonify({"error": "Error fetching data from Spotify"}), 500

        return jsonify(playlists)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


    
# Function to get music genres from OpenAI using GPT-4
def get_music_genres(user_input):
    try:
        # Construct the prompt to send to OpenAI in chat format
        messages = [
            {"role": "system", "content": "You are a helpful assistant that provides clear and structured responses."},
            {"role": "user", "content": f"Given the user's input: '{user_input}', suggest exactly three music genres. Provide only the genres, comma-delimited, with no extra commentary."}
        ]
        
        # Request OpenAI's chat completion model (gpt-4 or gpt-4-turbo)
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or use 'gpt-4-turbo'
            messages=messages,
            max_tokens=50,  # Limit to a short response
            temperature=0.7  # Control randomness (0.0 = deterministic, 1.0 = more creative)
        )
        
        # Extract the genres from the response
        genres = response['choices'][0]['message']['content'].strip().split(', ')
        return genres

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return []




@app.route('/logout')
def logout():
    # Clear the session data
    session.pop('spotify_token', None)
    session.pop('oauth_state', None)
    
    # Redirect to the login page after logout
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)


