(function () {
    var items = document.querySelectorAll('.reveal');

    if (!('IntersectionObserver' in window)) {
        items.forEach(function (el) { el.classList.add('revealed'); });
        window.__revealObserve = function (el) {
            if (el && el.nodeType === 1) el.classList.add('revealed');
        };
        return;
    }

    var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                io.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

    items.forEach(function (el) { io.observe(el); });

    window.__revealObserve = function (el) {
        if (el && el.nodeType === 1) io.observe(el);
    };
})();