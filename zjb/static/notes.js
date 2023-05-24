function save_notes(event) {
    const formdata = new FormData(event.target);
    const text = formdata.get('notes').trim();
    const url = event.target.action;

    fetch(url, {
        method: 'POST',
        body: new URLSearchParams(formdata)
    })
    .then(function(response) {
        if(response.ok) {
            toast('Saved successfully');

            let overlay = event.target.parentElement.parentElement;
            overlay.classList.remove('visible');

            let textarea = event.target.querySelector('textarea');
            textarea.innerHTML = text;  // Value for the [reset] button
            textarea.value = text;  // Content visible in the form

            let status = overlay.previousElementSibling;
            let icon = status.querySelector('span.notes');

            if(text && !icon) {
                let icon = document.createElement('span');
                icon.className = 'notes';
                status.appendChild(icon);
            } else if(!text && icon) {
                status.removeChild(icon);
            }
        } else {
            console.error('Response not ok', response);
            toast('Error ' + response.status, 'err');
        }
    })
    .catch (function(error) {
        console.error('Request failed:', error);
        toast('Request failed: (see console)', 'err');
    });

    event.preventDefault();
    event.stopPropagation();
    return false;
}

function close_notes(event) {
    let overlay = event.target.parentElement.parentElement;
    overlay.classList.remove('visible');
}

function bind_events_to_forms() {
    let forms = document.querySelectorAll('main table div.details form');
    for(const form of forms) {
        form.addEventListener('submit', save_notes);
        form.addEventListener('reset', close_notes);
    }
}
