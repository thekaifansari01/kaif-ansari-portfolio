(function () {
    var sections = document.querySelectorAll('section[id]');
    var topLinks = document.querySelectorAll('.nav-link');
    var bottomLinks = document.querySelectorAll('.bottom-nav .nav-item');

    function updateActive() {
        var scrollY = window.scrollY;
        var current = '';
        sections.forEach(function (section) {
            if (scrollY >= section.offsetTop - 200) {
                current = section.id;
            }
        });
        topLinks.forEach(function (link) {
            link.classList.toggle('active-nav', link.getAttribute('href') === '#' + current);
        });
        bottomLinks.forEach(function (link) {
            link.classList.toggle('active-nav', link.getAttribute('href') === '#' + current);
        });
    }

    window.addEventListener('scroll', updateActive, { passive: true });
    updateActive();

    bottomLinks.forEach(function (item) {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
})();