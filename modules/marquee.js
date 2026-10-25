(function () {
    var marquee = document.getElementById('marquee');
    if (!marquee) return;

    var row = marquee.querySelector('.marquee-row');
    if (!row) return;

    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            row.style.animationPlayState = 'paused';
        } else {
            row.style.animationPlayState = '';
        }
    });
})();