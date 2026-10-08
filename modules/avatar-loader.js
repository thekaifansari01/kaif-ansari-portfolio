(function () {
    var image = document.querySelector('.hero-photo img');
    if (!image) return;
    image.style.opacity = '0';
    image.style.transition = 'opacity 0.5s ease';

    var probe = new Image();
    probe.onload = function () {
        image.style.opacity = '1';
    };
    probe.onerror = function () {
        image.style.display = 'none';
    };
    probe.src = image.src;
})();