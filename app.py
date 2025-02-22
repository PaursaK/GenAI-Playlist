from flask import Flask, render_template, redirect, request, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
import secrets
import requests
import json
import openai
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
    #print(f'Access Token: {token["access_token"]}')  # Debugging line to check the access token
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

        # Ensure we have playlists
        if 'items' not in playlists_data:
            return "Error: Unable to retrieve playlists", 400

        playlists = playlists_data['items'][:3]  # Limit to first 3 playlists

        # Fetch tracks for each playlist
        for playlist in playlists:
            tracks_response = requests.get(playlist['tracks']['href'], headers=headers)
            tracks_data = tracks_response.json()
            playlist['tracks'] = [track['track'] for track in tracks_data.get('items', [])[:3]]  # First 3 tracks per playlist

        #print("Spotify Token:", session.get('spotify_token'))

        return render_template('home.html', 
                            user=profile_data,
                            playlists=playlists,
                            spotify_token=token['access_token'])  # Check if token is passed correctly
    except Exception as e:
        return f"Error fetching user data: {str(e)}", 400

@app.route('/generate', methods=['POST'])
def generate_playlist():
    import sys
    print("Raw request data:", request.get_data(), file=sys.stderr)  # Debugging the raw request body
    
    try:
        data = request.get_json()  # Parse JSON data from the request
        user_input = data.get('playlist_prompt')
        print(f"Extracted input: {user_input}", file=sys.stderr)
        
        if not user_input or user_input.strip() == "":
            print("Empty input received", file=sys.stderr)
            return jsonify({"error": "Empty input received"}), 400
        
        # Call the OpenAI API to get music genres
        genres = get_music_genres(user_input)

        print(genres)
        
        # Return the genres in the response
        return jsonify({'genres': genres}), 200
        
    except Exception as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return jsonify({"error": "Invalid JSON data"}), 400
    
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
        genres = response['choices'][0]['message']['content'].strip().split(',')
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


