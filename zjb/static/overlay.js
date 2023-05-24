function open_overlay(event) {
    let overlay = event.currentTarget.nextElementSibling;
    overlay.classList.add('visible');

    event.preventDefault();
    event.stopPropagation();
    return false;
}

function close_overlay() {
    let overlays = document.querySelectorAll('div.overlay.visible');
    for(const overlay of overlays) {
        overlay.classList.remove('visible');
        overlay.firstElementChild.firstElementChild.reset();
    }
}

function bind_links_to_overlays() {
    let links = document.querySelectorAll(
        'main table.view td a.status, main table.notes td a.edit'
    );
    for(const link of links) {
        link.addEventListener('click', open_overlay);
    }
}

function key_pressed(event) {
    const isNotCombinedKey = !(event.ctrlKey || event.altKey || event.shiftKey);
    if (event.key === 'Escape' && isNotCombinedKey) {
        close_overlay();
    }
}

document.addEventListener('keydown', key_pressed);
