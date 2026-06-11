const contactForm = document.getElementById('premiumContactForm');

if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const existingToast = document.querySelector('.success-toast');
        if (existingToast) existingToast.remove();
        
        const toast = document.createElement('div');
        toast.className = 'success-toast';
        toast.textContent = 'Message sent successfully! ✨';
        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--accent);
            color: var(--bg-primary);
            padding: 12px 24px;
            border-radius: 40px;
            font-weight: 500;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.remove(), 3000);
        contactForm.reset();
    });
}