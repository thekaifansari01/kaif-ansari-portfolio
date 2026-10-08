(function () {
    var toggle = document.querySelector('.theme-toggle');
    var html = document.documentElement;

    if (!toggle) return;

    toggle.addEventListener('click', function () {
        var current = html.getAttribute('data-theme');
        var next = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        try { localStorage.setItem('theme', next); } catch (e) {}
    });
})();