// Funções compartilhadas entre páginas
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
