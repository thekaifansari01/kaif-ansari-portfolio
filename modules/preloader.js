(function () {
    window.addEventListener('load', function () {
        var preloader = document.querySelector('.preloader');
        if (!preloader) return;
        setTimeout(function () {
            preloader.classList.add('fade-out');
            setTimeout(function () { preloader.remove(); }, 600);
        }, 600);
    });
})();