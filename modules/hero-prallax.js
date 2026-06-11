window.addEventListener('scroll', () => {
    const scrolled = window.scrollY;
    const hero = document.querySelector('.hero-premium');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});