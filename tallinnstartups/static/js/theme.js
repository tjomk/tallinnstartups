// Estonian Startup Jobs - Theme and Navigation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu functionality
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');

            // Update button icon
            const svg = mobileMenuButton.querySelector('svg path');
            if (mobileMenu.classList.contains('hidden')) {
                svg.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
                mobileMenuButton.setAttribute('aria-label', 'Open menu');
            } else {
                svg.setAttribute('d', 'M6 18L18 6M6 6l12 12');
                mobileMenuButton.setAttribute('aria-label', 'Close menu');
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
                mobileMenu.classList.add('hidden');
                const svg = mobileMenuButton.querySelector('svg path');
                svg.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
                mobileMenuButton.setAttribute('aria-label', 'Open menu');
            }
        });
    }

    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    const lightIcon = document.getElementById('theme-toggle-light-icon');
    const darkIcon = document.getElementById('theme-toggle-dark-icon');

    function updateThemeIcons(theme) {
        if (theme === 'dark') {
            lightIcon.classList.remove('hidden');
            darkIcon.classList.add('hidden');
        } else {
            lightIcon.classList.add('hidden');
            darkIcon.classList.remove('hidden');
        }
    }

    // Initialize icon state based on current theme
    const currentTheme = localStorage.getItem('theme') || 'light';
    updateThemeIcons(currentTheme);

    // Theme toggle click handler
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            if (newTheme === 'dark') {
                html.setAttribute('data-theme', 'dark');
                html.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            } else {
                html.removeAttribute('data-theme');
                html.classList.remove('dark-theme');
                localStorage.setItem('theme', 'light');
            }

            updateThemeIcons(newTheme);
        });
    }
});
