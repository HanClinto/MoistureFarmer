// window-management.js - Window utilities (fullscreen, navigation, window control)

/**
 * Enter or exit fullscreen mode
 */
function doFullscreen(enable) {
    const doc = document.documentElement;
    if (enable) {
        if (doc.requestFullscreen) {
            doc.requestFullscreen();
        } else if (doc.mozRequestFullScreen) { // Firefox
            doc.mozRequestFullScreen();
        } else if (doc.webkitRequestFullscreen) { // Chrome, Safari and Opera
            doc.webkitRequestFullscreen();
        } else if (doc.msRequestFullscreen) { // IE/Edge
            doc.msRequestFullscreen();
        }
        // Find all Maximize buttons and hide them
        const maximizeButtons = document.querySelectorAll('.title-bar-controls button[aria-label="Maximize"]');
        maximizeButtons.forEach(button => {
            button.classList.add('hidden');
        });
        // Show Restore button
        const restoreButtons = document.querySelectorAll('.title-bar-controls button[aria-label="Restore"]');
        restoreButtons.forEach(button => {
            button.classList.remove('hidden');
        });
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.mozCancelFullScreen) { // Firefox
            document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) { // Chrome, Safari and Opera
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) { // IE/Edge
            document.msExitFullscreen();
        }

        // Find all Maximize buttons and show them
        const maximizeButtons = document.querySelectorAll('.title-bar-controls button[aria-label="Maximize"]');
        maximizeButtons.forEach(button => {
            button.classList.remove('hidden');
        });
        // Hide Restore buttons
        const restoreButtons = document.querySelectorAll('.title-bar-controls button[aria-label="Restore"]');
        restoreButtons.forEach(button => {
            button.classList.add('hidden');
        });
    }
}

/**
 * Navigate to a specified URL
 */
function navigateTo(url) {
    console.log('Navigating to:', url);
    window.location.href = url;
}

// Export functions to global scope
window.doFullscreen = doFullscreen;
window.navigateTo = navigateTo;
