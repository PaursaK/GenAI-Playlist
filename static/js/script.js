// Toggle the user card dropdown visibility
function toggleUserCard() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
        console.log('Toggled dropdown:', dropdown.classList.contains('show')); // Debug line
    }
}

// Close dropdown if clicking outside
document.addEventListener('click', function(event) {
    const userCard = document.querySelector('.user-card');
    const dropdown = document.getElementById('userDropdown');
    
    if (!userCard.contains(event.target) && dropdown.classList.contains('show')) {
        dropdown.classList.remove('show');
    }
});

// Global variables for state tracking
let spotifyPlayer = null;
let spotifyDeviceId = null;
let currentlyPlayingUri = null;

// Wait for the Spotify Web Playback SDK to load
window.onSpotifyWebPlaybackSDKReady = () => {
    // Get the token from a global variable set in your template
    const token = document.getElementById('spotify-token').getAttribute('data-token');
    
    // Initialize the Player
    const player = new Spotify.Player({
        name: 'GenAI Playlist Player',
        getOAuthToken: cb => { cb(token); },
        volume: 0.5
    });
    
    // Store player reference globally
    spotifyPlayer = player;
    
    // Ready event
    player.addListener('ready', ({ device_id }) => {
        console.log('Ready with Device ID', device_id);
        spotifyDeviceId = device_id;
        
        // Transfer playback to this device
        fetch('https://api.spotify.com/v1/me/player', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                device_ids: [device_id],
                play: false
            })
        });
    });
    
    // Not ready event
    player.addListener('not_ready', ({ device_id }) => {
        console.log('Device ID has gone offline', device_id);
        spotifyDeviceId = null;
    });
    
    // Player state changed event - FIXED: defining updateButtonStates first
    player.addListener('player_state_changed', state => {
        if (state) {
            currentlyPlayingUri = state.track_window.current_track.uri;
            updatePlayerButtonStates(state.paused);
        }
    });
    
    // Error handling
    player.addListener('initialization_error', ({ message }) => console.error('Initialization Error:', message));
    player.addListener('authentication_error', ({ message }) => console.error('Authentication Error:', message));
    player.addListener('account_error', ({ message }) => console.error('Account Error:', message));
    player.addListener('playback_error', ({ message }) => console.error('Playback Error:', message));
    
    // Connect the player
    player.connect();
};

// FIXED: Function to update all button states based on player state
function updatePlayerButtonStates(isPaused) {
    document.querySelectorAll('.play-button').forEach(button => {
        const buttonUri = button.getAttribute('data-track-uri');
        const svg = button.querySelector('svg');
        
        if (buttonUri === currentlyPlayingUri) {
            svg.innerHTML = isPaused 
                ? '<path d="M6 4l12 8-12 8V4z"></path>' // play icon
                : '<path d="M6 5h4v14H6zM14 5h4v14h-4z"></path>'; // pause icon
        } else {
            svg.innerHTML = '<path d="M6 4l12 8-12 8V4z"></path>'; // play icon
        }
    });
}

// FIXED: Function to reset all play buttons except the active one
function resetAllPlayerButtons(activeUri) {
    document.querySelectorAll('.play-button').forEach(button => {
        const buttonUri = button.getAttribute('data-track-uri');
        if (buttonUri !== activeUri) {
            button.querySelector('svg').innerHTML = '<path d="M6 4l12 8-12 8V4z"></path>';
        }
    });
}

// Toggle play/pause with proper track control
function togglePlayPause(button) {
    const svg = button.querySelector("svg");
    const trackUri = button.getAttribute('data-track-uri');
    
    const pausePath = '<path d="M6 5h4v14H6zM14 5h4v14h-4z"></path>';
    const playPath = '<path d="M6 4l12 8-12 8V4z"></path>';
    
    // If no device is connected yet, show an error
    if (!spotifyDeviceId) {
        alert("Spotify player is not ready yet. Please wait a moment and try again.");
        return;
    }
    
    if (svg.innerHTML.includes("M6 4l12 8-12 8V4z")) {
        // It's the play icon, switch to pause and play this track
        svg.innerHTML = pausePath;
        playSong(trackUri);
    } else {
        // It's the pause icon, switch to play and pause playback
        svg.innerHTML = playPath;
        pausePlayback();
    }
}

// Play a specific song
async function playSong(uri) {
    console.log("Playing track:", uri);
    
    try {
        // FIXED: Using the correct function name
        resetAllPlayerButtons(uri);
        
        const token = document.getElementById('spotify-token').getAttribute('data-token');
        const response = await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${spotifyDeviceId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                uris: [uri]
            })
        });
        
        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }
        
        currentlyPlayingUri = uri;
    } catch (error) {
        console.error('Error playing track:', error);
    }
}

// Pause playback
async function pausePlayback() {
    console.log("Pausing playback");
    
    try {
        const token = document.getElementById('spotify-token').getAttribute('data-token');
        await fetch('https://api.spotify.com/v1/me/player/pause', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
    } catch (error) {
        console.error('Error pausing playback:', error);
    }
}