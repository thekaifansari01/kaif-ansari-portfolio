// Avatar Image Loader - Fixed
document.addEventListener('DOMContentLoaded', function() {
    const avatarImage = document.querySelector('.hero-avatar .avatar-image');
    const avatarIcon = document.querySelector('.hero-avatar .avatar-icon');
    
    if (!avatarImage) return;
    
    // Pehle icon ko visible rakho (default state)
    avatarIcon.style.display = 'flex';
    avatarImage.style.display = 'none';
    
    const img = new Image();
    img.onload = function() {
        // Image load ho gayi – icon hide, image show
        avatarIcon.style.display = 'none';
        avatarImage.style.display = 'block';
        avatarImage.classList.add('loaded');
        console.log('✅ Avatar image loaded');
    };
    
    img.onerror = function() {
        // Image nahi mili – icon show, image hide
        avatarIcon.style.display = 'flex';
        avatarImage.style.display = 'none';
        console.log('⚠️ Avatar image not found');
    };
    
    img.src = avatarImage.src;
});