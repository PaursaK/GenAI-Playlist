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

document.addEventListener('click', function(event) {
    if (event.target.closest('.download-btn')) { 
        const playlistCard = event.target.closest('.playlist-card');
        if (!playlistCard) return;

        // Extract playlist name and track URIs
        const playlistName = playlistCard.querySelector('h3').textContent;
        const trackUris = [...playlistCard.querySelectorAll('.play-button')]
            .map(button => button.getAttribute('data-track-uri'));

        // Send a request to the backend
        fetch('/download-playlist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: playlistName, track_uris: trackUris })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Playlist download started:", data.message);
            } else {
                console.error("Error downloading playlist:", data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    }
});



document.querySelector('.generate-button').addEventListener('click', function(event) {
    event.preventDefault();
    
    const inputText = document.querySelector('.prompt-input').value;

    if (inputText.trim() === "") {
        console.log("Please enter valid input.");
        return;
    }

    // Show loading indicator while fetching data
    document.querySelector('.loading-indicator').style.display = 'block';

    const requestData = {
        playlist_prompt: inputText
    };

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())  // Get the JSON response from Flask
    .then(data => {
        // Hide loading spinner
        document.querySelector('.loading-indicator').style.display = 'none';

        if (data.error) {
            console.error('Error:', data.error);
            return;
        }
    
        const playlistsGrid = document.querySelector('.playlists-grid');
        const placeholder = document.querySelector('.playlists-placeholder');
    
        // Hide placeholder when playlists are generated
        if (data.length > 0) {
            placeholder.style.display = 'none';
            playlistsGrid.classList.remove('hidden');
        }
        
        // Clear previous playlists before adding new ones
        playlistsGrid.innerHTML = '';  // Clear the current playlists (if any)

        // Render the playlists
        data.forEach(playlist => {
            const playlistDiv = document.createElement('div');
            playlistDiv.classList.add('playlist-card');
            
            // Template for the playlist HTML
            const playlistHtml = `

                <div class="download-btn-container">
                    <button class="download-btn">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 17l-5-5h3V3h4v9h3z"></path>
                        </svg>
                    </button>
                    <span class="download-info">Download</span>
                </div>

                ${playlist.images && playlist.images.length ? 
                    `<img src="${playlist.images[0].url}" alt="${playlist.name}" class="playlist-image">` 
                    : ''}
            
                <h3>${playlist.name}</h3>
            
                <ul class="track-list">
                    ${playlist.tracks.items.map(track => `  
                        <li>
                            <div class="track-info">
                                <div class="track-text">
                                    <div class="track-name">${track.name}</div>
                                    <div class="track-artist">${track.artist}</div>
                                </div>
                                <button class="play-button" 
                                        onclick="togglePlayPause(this)" 
                                        data-track-uri="${track.uri}">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M6 4l12 8-12 8V4z"></path>
                                    </svg>
                                </button>
                            </div>
                        </li>
                    `).join('')}
                </ul>
            `;

            // Inject playlist HTML into the playlist card div
            playlistDiv.innerHTML = playlistHtml;

            // Append the playlist card to the grid
            playlistsGrid.appendChild(playlistDiv);
        });
    })
    .catch(error => {
        console.error('Error:', error);
        document.querySelector('.loading-indicator').style.display = 'none';
    });
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
                uris: ["spotify:track:4t9vB7wIKWE5jIhjcztmmd"],  // Use a valid Spotify track URI
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