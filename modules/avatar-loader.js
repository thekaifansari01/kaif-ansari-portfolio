// modules/avatar-loader.js
(function(){
    const avatarImage = document.querySelector('.hero-avatar .avatar-image');
    const avatarIcon = document.querySelector('.hero-avatar .avatar-icon');
    if (!avatarImage) return;

    if (avatarIcon) avatarIcon.style.display = 'flex';
    avatarImage.style.display = 'none';
    avatarImage.classList.remove('loaded');

    const img = new Image();
    img.onload = function() {
        if (avatarIcon) avatarIcon.style.display = 'none';
        avatarImage.style.display = 'block';
        avatarImage.classList.add('loaded');
    };
    img.onerror = function() {
        if (avatarIcon) avatarIcon.style.display = 'flex';
        avatarImage.style.display = 'none';
        avatarImage.classList.remove('loaded');
    };
    img.src = avatarImage.src;
})();