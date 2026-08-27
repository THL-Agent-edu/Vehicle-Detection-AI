// Theme toggle logic
document.addEventListener('DOMContentLoaded', () => {
    // Check local storage for theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-mode');
    }

    // Find the toggle button(s)
    const themeToggles = document.querySelectorAll('.theme-toggle');
    
    themeToggles.forEach(toggle => {
        // Update icon initially if needed
        updateIcon(toggle);

        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            document.body.classList.toggle('light-mode');
            
            const isLight = document.body.classList.contains('light-mode');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
            
            // Update all icons
            themeToggles.forEach(t => updateIcon(t));
        });
    });

    function updateIcon(element) {
        const icon = element.querySelector('i');
        if (!icon) {
            // If the element itself is the icon
            if (element.tagName === 'I') {
                if (document.body.classList.contains('light-mode')) {
                    element.classList.remove('ph-sun');
                    element.classList.add('ph-moon');
                } else {
                    element.classList.remove('ph-moon');
                    element.classList.add('ph-sun');
                }
            }
            return;
        }

        // If icon is inside
        if (document.body.classList.contains('light-mode')) {
            icon.classList.remove('ph-sun');
            icon.classList.add('ph-moon');
        } else {
            icon.classList.remove('ph-moon');
            icon.classList.add('ph-sun');
        }
    }
});
