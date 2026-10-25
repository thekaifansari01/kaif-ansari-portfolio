(function () {
    if (window.matchMedia('(hover: none)').matches) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const glyphs = '!<>-_\\/[]{}=+*^?#';
    const targets = document.querySelectorAll('.nav-link, .footer-links a');

    targets.forEach(function (el) {
        const original = el.textContent;
        let timer = null;

        el.addEventListener('mouseenter', function () {
            if (timer) clearInterval(timer);
            let frame = 0;
            const total = original.length * 4;
            timer = setInterval(function () {
                el.textContent = original
                    .split('')
                    .map(function (ch, i) {
                        if (ch === ' ') return ' ';
                        if (i < frame / 4) return original[i];
                        return glyphs[Math.floor(Math.random() * glyphs.length)];
                    })
                    .join('');
                frame++;
                if (frame > total) {
                    clearInterval(timer);
                    timer = null;
                    el.textContent = original;
                }
            }, 30);
        });

        el.addEventListener('mouseleave', function () {
            if (timer) {
                clearInterval(timer);
                timer = null;
            }
            el.textContent = original;
        });
    });
})();