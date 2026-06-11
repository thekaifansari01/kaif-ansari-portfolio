const yearSpan = document.querySelector('.footer-copyright p');
if (yearSpan) {
    yearSpan.innerHTML = yearSpan.innerHTML.replace('2025', new Date().getFullYear());
}