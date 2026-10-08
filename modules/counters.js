(function () {
    var counters = document.querySelectorAll('.stat-number');
    if (!counters.length || !('IntersectionObserver' in window)) return;

    var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            var el = entry.target;
            var target = parseInt(el.getAttribute('data-target'), 10) || 0;
            var current = 0;
            var step = Math.max(1, Math.floor(target / 40));
            var tick = function () {
                current += step;
                if (current >= target) {
                    el.textContent = target;
                    return;
                }
                el.textContent = current;
                setTimeout(tick, 30);
            };
            tick();
            io.unobserve(el);
        });
    }, { threshold: 0.5 });

    counters.forEach(function (c) { io.observe(c); });
})();