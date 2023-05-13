function toast(text, status='ok') {
    let box = document.createElement('div');
    box.classList.add('toast');

    document.body.appendChild(box);

    box.innerHTML = text;
    box.classList.add(status);
    box.classList.add('visible');

    setTimeout(function() {
        box.classList.remove('visible');
        document.body.removeChild(box);
    }, 3000);
}
