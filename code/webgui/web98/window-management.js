// window-management.js - Window utilities (fullscreen, navigation, window control, window creation)

/**
 * Create a new dialog window with persistent position/size storage
 * @param {Object} options - Window configuration options
 * @param {string} options.id - Unique window ID
 * @param {string} options.title - Window title
 * @param {string} options.content - HTML content for window body
 * @param {number} [options.width=400] - Default width in pixels
 * @param {number} [options.height=300] - Default height in pixels
 * @param {number} [options.left] - Default left position (if not restored)
 * @param {number} [options.top] - Default top position (if not restored)
 * @param {boolean} [options.resizable=true] - Whether window is resizable
 * @param {boolean} [options.draggable=true] - Whether window is draggable
 * @param {Function} [options.onClose] - Callback when window is closed
 * @returns {HTMLElement} The created window element
 */
function createWindow(options) {
    const {
        id,
        title,
        content = '',
        width = 400,
        height = 300,
        left,
        top,
        resizable = true,
        draggable = true,
        onClose
    } = options;

    // Check if window already exists
    let win = document.getElementById(id);
    if (win) {
        showWindow(id);
        bringToFront(win);
        return win;
    }

    // Create window element
    win = document.createElement('div');
    win.id = id;
    win.className = 'window';
    if (draggable) win.classList.add('draggable');
    if (resizable) win.classList.add('resizeable');
    
    win.innerHTML = `
        <div class="title-bar">
            <div class="title-bar-text">${title}</div>
            <div class="title-bar-controls">
                <button aria-label="Close"></button>
            </div>
        </div>
        ${content}
    `;

    document.body.appendChild(win);

    // Load saved position/size or use defaults
    const saved = loadWindowState(id);
    if (saved) {
        if (saved.left !== undefined) win.style.left = saved.left + 'px';
        if (saved.top !== undefined) win.style.top = saved.top + 'px';
        if (saved.width !== undefined) win.style.width = saved.width + 'px';
        if (saved.height !== undefined) win.style.height = saved.height + 'px';
    } else {
        // Apply defaults
        win.style.width = width + 'px';
        win.style.height = height + 'px';
        if (left !== undefined) win.style.left = left + 'px';
        if (top !== undefined) win.style.top = top + 'px';
        
        // Center if no position specified
        if (left === undefined && top === undefined) {
            const rect = win.getBoundingClientRect();
            win.style.left = Math.max(0, (window.innerWidth - rect.width) / 2) + 'px';
            win.style.top = Math.max(0, (window.innerHeight - rect.height) / 2) + 'px';
        }
    }

    // Wire close button
    const closeButton = win.querySelector('.title-bar-controls button[aria-label="Close"]');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            saveWindowState(id, win);
            win.classList.add('hidden');
            if (onClose) onClose();
        });
    }

    // Make window interactive
    if (resizable && typeof resizeableElement === 'function') {
        resizeableElement(win);
    }
    if (draggable && typeof draggableElement === 'function') {
        draggableElement(win);
    }
    if (typeof bringableToFront === 'function') {
        bringableToFront(win);
    }

    // Save state on window move/resize (debounced)
    let saveTimer;
    const debouncedSave = () => {
        clearTimeout(saveTimer);
        saveTimer = setTimeout(() => saveWindowState(id, win), 500);
    };

    // Monitor for position/size changes
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.type === 'attributes' && 
                (mutation.attributeName === 'style')) {
                debouncedSave();
                break;
            }
        }
    });
    observer.observe(win, { attributes: true, attributeFilter: ['style'] });

    // Save initial state
    saveWindowState(id, win);

    return win;
}

/**
 * Save window position and size to localStorage
 */
function saveWindowState(windowId, windowElement) {
    try {
        const state = {
            left: windowElement.offsetLeft,
            top: windowElement.offsetTop,
            width: windowElement.offsetWidth,
            height: windowElement.offsetHeight
        };
        localStorage.setItem(`window_${windowId}`, JSON.stringify(state));
    } catch (e) {
        console.warn('Failed to save window state:', e);
    }
}

/**
 * Load window position and size from localStorage
 */
function loadWindowState(windowId) {
    try {
        const saved = localStorage.getItem(`window_${windowId}`);
        return saved ? JSON.parse(saved) : null;
    } catch (e) {
        console.warn('Failed to load window state:', e);
        return null;
    }
}

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
window.createWindow = createWindow;
window.saveWindowState = saveWindowState;
window.loadWindowState = loadWindowState;
window.doFullscreen = doFullscreen;
window.navigateTo = navigateTo;
