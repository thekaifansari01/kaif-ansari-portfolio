// modules/avatar-loader.js
(function(){
    const avatarImage = document.querySelector('.hero-avatar .avatar-image');
    const avatarIcon = document.querySelector('.hero-avatar .avatar-icon');
    if (!avatarImage) return;

    if (window.innerWidth <= 968) {
        avatarImage.style.display = 'none';
        if (avatarIcon) avatarIcon.style.display = 'flex';
        return;
    }

    avatarIcon.style.display = 'flex';
    avatarImage.style.display = 'none';

    const img = new Image();
    img.onload = function() {
        avatarIcon.style.display = 'none';
        avatarImage.style.display = 'block';
        avatarImage.classList.add('loaded');
    };
    img.onerror = function() {
        avatarIcon.style.display = 'flex';
        avatarImage.style.display = 'none';
    };
    img.src = avatarImage.src;
})();