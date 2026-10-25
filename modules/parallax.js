(function () {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const photo = document.querySelector('.hero-photo');
    if (!photo) return;

    let raf = null;
    function update() {
        raf = null;
        const py = Math.min(window.scrollY * 0.12, 60);
        photo.style.setProperty('--hero-py', py + 'px');
    }

    window.addEventListener('scroll', function () {
        if (!raf) raf = requestAnimationFrame(update);
    }, { passive: true });
})();