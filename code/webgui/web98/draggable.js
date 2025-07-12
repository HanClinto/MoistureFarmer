
// Bringable to front
var newTop = 1000;

function bringableToFront(elmnt) {
  // Ensure that when clicked, the element is brought to the front
  elmnt.addEventListener('mousedown', function() {
    bringToFront(elmnt);
  });
}

function bringToFront(elmnt) {
    // Ensure the window is brought to the front
    elmnt.style.zIndex = ++newTop;
}

// Draggable / moveable elements
function draggableElement(elmnt) {
    const bar = elmnt.querySelector('.title-bar');
    if (!bar) return;
    let dragTarget = null, offsetX = 0, offsetY = 0;
    bar.addEventListener('mousedown', function(e) {
        dragTarget = elmnt;
        const rect = dragTarget.getBoundingClientRect();
        offsetX = e.clientX - rect.left;
        offsetY = e.clientY - rect.top;
        document.body.style.userSelect = 'none';
    });
    document.addEventListener('mousemove', function(e) {
        if (dragTarget) {
            dragTarget.style.left = (e.clientX - offsetX) + 'px';
            dragTarget.style.top = (e.clientY - offsetY) + 'px';
            // Ensure the window stays within the viewport
            const rect = dragTarget.getBoundingClientRect();
            if (rect.left < 0) dragTarget.style.left = '0px';
            if (rect.top < 0) dragTarget.style.top = '0px';
            if (rect.right > window.innerWidth) dragTarget.style.left = (window.innerWidth - rect.width)
                + 'px';
            if (rect.bottom > window.innerHeight) dragTarget.style.top = (window.innerHeight - rect.height)
                + 'px';
        }
    });
    document.addEventListener('mouseup', function() {
        dragTarget = null;
        document.body.style.userSelect = '';
    });
}


// Resizeable elements
function resizeableElement(elmnt) {
    const handle = document.createElement('div');
    handle.className = 'resize-handle';
    elmnt.appendChild(handle);

    let resizing = false, startX, startY, startW, startH;
    handle.addEventListener('mousedown', function(e) {
        e.stopPropagation();
        resizing = true;
        startX = e.clientX;
        startY = e.clientY;
        const rect = elmnt.getBoundingClientRect();
        startW = rect.width;
        startH = rect.height;
        document.body.style.userSelect = 'none';
    });
    document.addEventListener('mousemove', function(e) {
        if (resizing) {
            elmnt.style.width = Math.max(150, startW + (e.clientX - startX)) + 'px';
            elmnt.style.height = Math.max(80, startH + (e.clientY - startY)) + 'px';
        }
    });
    document.addEventListener('mouseup', function() {
        resizing = false;
        document.body.style.userSelect = '';
    });
}
