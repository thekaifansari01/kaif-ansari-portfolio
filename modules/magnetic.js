(function () {
    if (window.matchMedia('(hover: none)').matches) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const els = document.querySelectorAll('.btn-primary, .btn-ghost, .nav-resume, .social-link');
    const strength = 0.3;

    els.forEach(function (el) {
        el.addEventListener('mousemove', function (e) {
            const rect = el.getBoundingClientRect();
            const cx = rect.left + rect.width / 2;
            const cy = rect.top + rect.height / 2;
            el.style.setProperty('--mag-x', ((e.clientX - cx) * strength) + 'px');
            el.style.setProperty('--mag-y', ((e.clientY - cy) * strength) + 'px');
        });

        el.addEventListener('mouseleave', function () {
            el.style.setProperty('--mag-x', '0px');
            el.style.setProperty('--mag-y', '0px');
        });
    });
})();