// Theme Management
function setTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById('themeText').innerHTML = 'Light Mode';
        localStorage.setItem('theme', 'dark');
        fetch('/api/set-theme', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({theme: 'dark'})
        });
    } else {
        document.body.classList.remove('dark-mode');
        document.getElementById('themeText').innerHTML = 'Dark Mode';
        localStorage.setItem('theme', 'light');
        fetch('/api/set-theme', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({theme: 'light'})
        });
    }
}

function toggleTheme() {
    const isDark = document.body.classList.contains('dark-mode');
    setTheme(isDark ? 'light' : 'dark');
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
setTheme(savedTheme);