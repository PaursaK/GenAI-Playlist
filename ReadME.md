# Gen AI Spotify Playlist Generator

## Overview

The Gen AI Spotify Playlist Generator is a full-stack web application that allows users to generate custom Spotify playlists based on text prompts. Utilizing OpenAI's API for intelligent playlist curation and the Spotify API for music streaming and playlist management, this app provides a seamless experience for music discovery.

## Features

- AI-Generated Playlists: Enter a text prompt to generate a curated playlist.

- Spotify Integration: Securely log in with Spotify to create and save playlists.

- Genre Analysis: Uses AI to understand user input and map it to relevant music genres.

- Community Trends: Tracks trending searches to display popular music preferences.

- Interactive Word Cloud: Displays trending genres in a visually engaging way.

## Tech Stack

### Frontend

-  HTML, CSS, JavaScript

- Fetch API for asynchronous requests

### Backend

- Python (Flask)

- SQLite for database management

- OpenAI API for text processing

- Spotify API for playlist creation and music retrieval

## Setup Instructions

### Prerequisites

- Python 3.x

- Spotify Developer Account

- OpenAI API Key

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/gen-ai-spotify.git
   cd gen-ai-spotify

2. Create a virtual environment and install dependencies
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt

3. Set up environment variables:
   ```sh
   export SPOTIFY_CLIENT_ID='your_spotify_client_id'
   export SPOTIFY_CLIENT_SECRET='your_spotify_client_secret'
   export OPENAI_API_KEY='your_openai_api_key'

4. Run the backend server:
   ```sh
   flask run

## Usage

1. Navigate to the web app in your browser.

2. Log in with Spotify to grant access.

3. Enter a prompt describing the type of playlist you want.

4. View the generated playlist and save it to your Spotify account.

5. Explore trending searches and genre word clouds.

## Future Improvements

- Enhance AI prompts for better genre-based recommendations.

- Implement user profile analytics.

- Optimize the UI/UX for a better user experience.

- Expand database support for caching and analytics.

## License

MIT License

## Contributors

- Paursa Kamalian - Creator & Developer

Feel free to contribute by submitting pull requests or opening issues!
