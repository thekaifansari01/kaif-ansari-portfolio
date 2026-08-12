// modules/hero-parallax.js
(function(){
    const hero = document.querySelector('.hero-premium');
    if (!hero) return;
    let ticking = false;
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                if (window.innerWidth > 968) {
                    const scrolled = window.scrollY;
                    hero.style.transform = 'translateY(' + (scrolled * 0.3) + 'px)';
                } else {
                    hero.style.transform = '';
                }
                ticking = false;
            });
            ticking = true;
        }
    });
})();