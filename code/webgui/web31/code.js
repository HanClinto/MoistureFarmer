// New window: show and bring to top
function newWindow(element) {
    $(element).show();
    $(element).selectWindow();

    if (element == '#doom') {
    	loadDoom();
    }
}


// Load DOOM, because we can
function loadDoom() {
	$.getScript('https://js-dos.com/6.22/current/js-dos.js', function() {
		Dos(document.getElementById("doomcanvas"), {
	        wdosboxUrl: "https://js-dos.com/6.22/current/wdosbox.js",
	        cycles: 1000,
	        autolock: false,
	    }).ready(function (fs, main) {
	      fs.extract("https://js-dos.com/cdn/upload/DOOM-@evilution.zip").then(function () {
	        main(["-c", "cd DOOM", "-c", "DOOM.EXE"]).then(function (ci) {
	            window.ci = ci;
	        });
	      });
	    });
	});
}

// --- SSE subscription and live update logic ---
let latestGameState = null;

function subscribeToGameState() {
    const evtSource = new EventSource('/events');
    evtSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        latestGameState = data;
        renderEntityList(data.entities);
    };
}

// --- Render entity list as buttons/icons ---
function renderEntityList(entities) {
    let container = document.getElementById('entity-list');
    if (!container) {
        // Create the window if it doesn't exist
        container = document.createElement('div');
        container.id = 'entity-list';
        container.className = 'window';
        container.style = 'position: absolute; top: 60px; left: 60px; width: 320px; height: 400px; z-index: 10;';
        container.innerHTML = `
            <div class="windowheader">
                <div class="windowclose"></div>
                <div class="windowtitle">Entities</div>
            </div>
            <div class="windowinner" style="overflow-y: auto; height: 90%">
                <div id="entity-list-inner"></div>
            </div>
        `;
        document.body.appendChild(container);
        // Close logic
        container.querySelector('.windowclose').ondblclick = function() {
            container.style.display = 'none';
        };
    }
    const inner = container.querySelector('#entity-list-inner');
    inner.innerHTML = '';
    for (const [id, entity] of Object.entries(entities)) {
        const btn = document.createElement('button');
        btn.textContent = entity.name || entity.model || id;
        btn.className = 'entity-btn';
        btn.onclick = () => openEntityModal(entity);
        // Optionally show sprite
        if (entity.sprite) {
            const img = document.createElement('img');
            img.src = '/sprites/' + entity.sprite;
            img.alt = 'sprite';
            img.style = 'height: 32px; vertical-align: middle; margin-right: 8px;';
            btn.prepend(img);
        }
        inner.appendChild(btn);
        inner.appendChild(document.createElement('br'));
    }
}

// --- Modal dialog for entity details ---
function openEntityModal(entity) {
    const modalId = 'modal-entity-' + entity.id;
    let modal = document.getElementById(modalId);
    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'window';
        modal.style = 'position: absolute; top: 120px; left: 120px; width: 400px; height: 500px; z-index: 20;';
        modal.innerHTML = `
            <div class="windowheader">
                <div class="windowclose"></div>
                <div class="windowtitle">${entity.name || entity.model || entity.id}</div>
            </div>
            <div class="windowinner" style="overflow-y: auto; height: 90%">
                <div id="entity-modal-content-${entity.id}"></div>
            </div>
        `;
        document.body.appendChild(modal);
        // Close logic
        modal.querySelector('.windowclose').ondblclick = function() {
            modal.style.display = 'none';
        };
        // Drag/bring to top
        $(modal).draggable({ handle: 'div.windowtitle' });
        $(modal).mousedown(function() { $(this).selectWindow(); });
    }
    // Render content
    const content = modal.querySelector(`#entity-modal-content-${entity.id}`);
    content.innerHTML = '';
    // Sprite
    if (entity.sprite) {
        const img = document.createElement('img');
        img.src = '/sprites/' + entity.sprite;
        img.alt = 'sprite';
        img.style = 'height: 64px; display: block; margin: 0 auto 8px auto;';
        content.appendChild(img);
    }
    // JSON view
    content.appendChild(renderCollapsibleJson(entity));
    // If chassis, show components
    if (entity.slots) {
        const compDiv = document.createElement('div');
        compDiv.innerHTML = '<b>Components:</b><br>';
        for (const [slotId, slot] of Object.entries(entity.slots)) {
            if (slot.component) {
                const compBtn = document.createElement('button');
                compBtn.textContent = slotId + ': ' + (slot.component.name || slot.component.type || slot.component.id);
                compBtn.onclick = () => openComponentModal(slot.component, entity.id + '-' + slotId);
                // Sprite for component
                if (slot.component.sprite) {
                    const img = document.createElement('img');
                    img.src = '/sprites/' + slot.component.sprite;
                    img.alt = 'sprite';
                    img.style = 'height: 24px; vertical-align: middle; margin-right: 4px;';
                    compBtn.prepend(img);
                }
                compDiv.appendChild(compBtn);
                compDiv.appendChild(document.createElement('br'));
            }
        }
        content.appendChild(compDiv);
    }
    modal.style.display = 'block';
    $(modal).selectWindow();
}

// --- Modal dialog for component details ---
function openComponentModal(component, uniqueId) {
    const modalId = 'modal-component-' + uniqueId;
    let modal = document.getElementById(modalId);
    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'window';
        modal.style = 'position: absolute; top: 180px; left: 180px; width: 350px; height: 400px; z-index: 30;';
        modal.innerHTML = `
            <div class="windowheader">
                <div class="windowclose"></div>
                <div class="windowtitle">${component.name || component.type || component.id}</div>
            </div>
            <div class="windowinner" style="overflow-y: auto; height: 90%">
                <div id="component-modal-content-${uniqueId}"></div>
            </div>
        `;
        document.body.appendChild(modal);
        // Close logic
        modal.querySelector('.windowclose').ondblclick = function() {
            modal.style.display = 'none';
        };
        // Drag/bring to top
        $(modal).draggable({ handle: 'div.windowtitle' });
        $(modal).mousedown(function() { $(this).selectWindow(); });
    }
    // Render content
    const content = modal.querySelector(`#component-modal-content-${uniqueId}`);
    content.innerHTML = '';
    // Sprite
    if (component.sprite) {
        const img = document.createElement('img');
        img.src = '/sprites/' + component.sprite;
        img.alt = 'sprite';
        img.style = 'height: 48px; display: block; margin: 0 auto 8px auto;';
        content.appendChild(img);
    }
    // JSON view
    content.appendChild(renderCollapsibleJson(component));
    modal.style.display = 'block';
    $(modal).selectWindow();
}

// --- Simple collapsible JSON viewer ---
function renderCollapsibleJson(obj, level=0) {
    const container = document.createElement('div');
    for (const key in obj) {
        if (!obj.hasOwnProperty(key)) continue;
        const val = obj[key];
        const row = document.createElement('div');
        row.style.marginLeft = (level * 12) + 'px';
        if (typeof val === 'object' && val !== null && !Array.isArray(val)) {
            const toggle = document.createElement('span');
            toggle.textContent = '[+] ';
            toggle.style.cursor = 'pointer';
            const keySpan = document.createElement('span');
            keySpan.textContent = key + ': ';
            row.appendChild(toggle);
            row.appendChild(keySpan);
            const child = renderCollapsibleJson(val, level + 1);
            child.style.display = 'none';
            toggle.onclick = function() {
                if (child.style.display === 'none') {
                    child.style.display = 'block';
                    toggle.textContent = '[-] ';
                } else {
                    child.style.display = 'none';
                    toggle.textContent = '[+] ';
                }
            };
            row.appendChild(child);
        } else {
            row.textContent = key + ': ' + val;
        }
        container.appendChild(row);
    }
    return container;
}

// --- On page load, subscribe to game state ---
window.addEventListener('DOMContentLoaded', function() {
    subscribeToGameState();
});

$( function() {
    // Window drag
    $( ".window" ).draggable({ handle: "div.windowtitle" });

    // Window resize
    $( ".window" ).resizable({ handles: "all", alsoresize: ".windowinner" });

    // Window close
    $('.windowclose').on("dblclick", function () { $(this).parents('div.window').hide(); });

    // Window click-to-bring-to-top
    (function() {
        var highest = 100;

        $.fn.selectWindow = function() {
            // Make top
            this.css('z-index', ++highest);
            // Make this window selected and others not
            this.addClass('selectedwindow');
            $('.window').not(this).each(function(){
                $(this).removeClass('selectedwindow');
             });
        };
    })();
    $('.window').mousedown(function() {
        $(this).selectWindow();
    });

    // Icon single click
    $('.icon').click(function() {
      $(this).find('p').toggleClass('highlight');
    });
} );
