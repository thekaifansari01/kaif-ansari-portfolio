window.addEventListener('load', () => {
    const preloader = document.querySelector('.preloader');
    setTimeout(() => {
        if (preloader) preloader.classList.add('fade-out');
    }, 500);
});