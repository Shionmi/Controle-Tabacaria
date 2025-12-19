// Funções compartilhadas entre páginas

// Setup CSRF token for all fetch requests
let csrfToken = null;

// Get CSRF token from meta tag or fetch it
function getCSRFToken() {
    if (csrfToken) return Promise.resolve(csrfToken);
    
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        csrfToken = metaToken.getAttribute('content');
        return Promise.resolve(csrfToken);
    }
    
    return fetch('/api/csrf-token')
        .then(r => r.json())
        .then(data => {
            csrfToken = data.csrf_token;
            return csrfToken;
        })
        .catch(err => {
            console.error('Error fetching CSRF token:', err);
            return null;
        });
}

// Enhanced fetch with CSRF token
async function secureFetch(url, options = {}) {
    const token = await getCSRFToken();
    
    options.headers = options.headers || {};
    if (token && ['POST', 'PUT', 'DELETE', 'PATCH'].includes((options.method || 'GET').toUpperCase())) {
        options.headers['X-CSRFToken'] = token;
    }
    
    return fetch(url, options);
}

// Export secure fetch globally
window.secureFetch = secureFetch;

function toggleFullScreen() {
    const doc = document;
    const docEl = document.documentElement;
    const isFull = !!(doc.fullscreenElement || doc.webkitFullscreenElement || doc.mozFullScreenElement || doc.msFullscreenElement);

    if (!isFull) {
        const request = docEl.requestFullscreen || docEl.webkitRequestFullscreen || docEl.mozRequestFullScreen || docEl.msRequestFullscreen;
        if (request) request.call(docEl);
    } else {
        const exit = doc.exitFullscreen || doc.webkitExitFullscreen || doc.mozCancelFullScreen || doc.msExitFullscreen;
        if (exit) exit.call(doc);
    }
}

function updateFullScreenButton() {
    const btn = document.getElementById('fullscreenBtn');
    const floating = document.getElementById('floatingFullscreen');
    const doc = document;
    const isFull = !!(doc.fullscreenElement || doc.webkitFullscreenElement || doc.mozFullScreenElement || doc.msFullscreenElement);
    if (btn) btn.textContent = isFull ? '⤢ Sair Tela Cheia' : '⛶ Tela Cheia';
    if (floating) floating.textContent = isFull ? '⤢' : '⛶';
}

document.addEventListener('fullscreenchange', updateFullScreenButton);
document.addEventListener('webkitfullscreenchange', updateFullScreenButton);
document.addEventListener('mozfullscreenchange', updateFullScreenButton);
document.addEventListener('MSFullscreenChange', updateFullScreenButton);

document.addEventListener('DOMContentLoaded', () => {
    updateFullScreenButton();
});

// export to window
window.appCommon = { toggleFullScreen, updateFullScreenButton };
