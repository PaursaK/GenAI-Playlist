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