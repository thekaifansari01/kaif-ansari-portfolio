const cursorFollower = document.querySelector('.cursor-follower');
const cursorDot = document.querySelector('.cursor-dot-premium');

if (cursorFollower && cursorDot) {
    document.addEventListener('mousemove', (e) => {
        if (window.innerWidth > 968) {
            cursorFollower.style.transform = `translate(${e.clientX - 20}px, ${e.clientY - 20}px)`;
            cursorDot.style.transform = `translate(${e.clientX - 3}px, ${e.clientY - 3}px)`;
        }
    });

    const clickables = document.querySelectorAll('a, button, .work-card, .skill-category');
    clickables.forEach(el => {
        el.addEventListener('mouseenter', () => {
            if (window.innerWidth > 968) {
                cursorFollower.style.transform = `scale(1.5)`;
                cursorFollower.style.opacity = '0.3';
            }
        });
        el.addEventListener('mouseleave', () => {
            if (window.innerWidth > 968) {
                cursorFollower.style.transform = `scale(1)`;
                cursorFollower.style.opacity = '0.6';
            }
        });
    });
}