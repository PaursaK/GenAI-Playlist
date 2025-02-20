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

function togglePlayPause(button) {
    let svg = button.querySelector("svg");

    let pause = '<path d="M6 5h4v14H6zM14 5h4v14h-4z"></path>';
    let play = '<path d="M6 4l12 8-12 8V4z"></path>';
    
    if (svg.innerHTML.includes("M6 4l12 8-12 8V4z")) { 
        // If it's the play icon, switch to pause
        svg.innerHTML = pause;
    } else {
        // If it's the pause icon, switch to play
        svg.innerHTML = play;
    }
}