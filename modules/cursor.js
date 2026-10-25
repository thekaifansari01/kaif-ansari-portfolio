(function () {
    if (window.matchMedia('(hover: none)').matches) return;
    if (window.matchMedia('(pointer: coarse)').matches) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var dot = document.createElement('div');
    var ring = document.createElement('div');
    dot.className = 'cursor-dot';
    ring.className = 'cursor-ring';
    document.body.appendChild(dot);
    document.body.appendChild(ring);
    document.body.classList.add('has-custom-cursor');

    var mx = window.innerWidth / 2;
    var my = window.innerHeight / 2;
    var dx = mx, dy = my;
    var rx = mx, ry = my;
    var active = false;

    var STATE_CLASSES = ['is-link', 'is-card', 'is-text', 'is-image'];

    var LINK_SEL = 'a, button, .theme-toggle, .nav-link, .nav-resume, .work-cta, .social-link, .footer-links a, .nav-logo, .bottom-nav .nav-item';
    var CARD_SEL = '.work-card, .marquee-item, .stat, .about-note, .contact-terminal, .hero-prompt, .work-tag, .work-status';
    var TEXT_SEL = 'input, textarea, [contenteditable="true"]';
    var IMAGE_SEL = '.hero-photo';

    function clearState() {
        for (var i = 0; i < STATE_CLASSES.length; i++) {
            dot.classList.remove(STATE_CLASSES[i]);
            ring.classList.remove(STATE_CLASSES[i]);
        }
    }

    function setState(target) {
        if (!target || !target.closest) {
            clearState();
            return;
        }
        clearState();
        if (target.closest(TEXT_SEL)) {
            dot.classList.add('is-text');
            ring.classList.add('is-text');
        } else if (target.closest(IMAGE_SEL)) {
            dot.classList.add('is-image');
            ring.classList.add('is-image');
        } else if (target.closest(LINK_SEL)) {
            dot.classList.add('is-link');
            ring.classList.add('is-link');
        } else if (target.closest(CARD_SEL)) {
            dot.classList.add('is-card');
            ring.classList.add('is-card');
        }
    }

    document.addEventListener('mousemove', function (e) {
        mx = e.clientX;
        my = e.clientY;
        if (!active) {
            active = true;
            dot.classList.add('is-visible');
            ring.classList.add('is-visible');
        }
    });

    document.addEventListener('mouseleave', function () {
        active = false;
        dot.classList.remove('is-visible');
        ring.classList.remove('is-visible');
    });

    document.addEventListener('mousedown', function () {
        dot.classList.add('is-clicking');
        ring.classList.add('is-clicking');
    });

    document.addEventListener('mouseup', function () {
        dot.classList.remove('is-clicking');
        ring.classList.remove('is-clicking');
    });

    document.addEventListener('mouseover', function (e) {
        setState(e.target);
    });

    document.addEventListener('mouseout', function (e) {
        if (!e.relatedTarget) clearState();
    });

    function tick() {
        dx += (mx - dx) * 0.5;
        dy += (my - dy) * 0.5;
        rx += (mx - rx) * 0.18;
        ry += (my - ry) * 0.18;
        dot.style.translate = dx + 'px ' + dy + 'px';
        ring.style.translate = rx + 'px ' + ry + 'px';
        requestAnimationFrame(tick);
    }
    tick();
})();