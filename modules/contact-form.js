const contactForm = document.getElementById('premiumContactForm');

if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Token capture
        const tokenInput = document.querySelector('[name="cf-turnstile-response"]');
        const token = tokenInput ? tokenInput.value : null;

        if (!token || token.length < 10) {
            showToast('⚠️ Please complete the CAPTCHA verification first.');
            return;
        }

        const name = document.getElementById('premiumName').value;
        const email = document.getElementById('premiumEmail').value;
        const message = document.getElementById('premiumMessage').value;

        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '⏳ Sending...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, message, token })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                showToast('✅ ' + (result.message || 'Message sent!'));
                contactForm.reset();
                if (typeof turnstile !== 'undefined') turnstile.reset();
            } else {
                showToast('❌ ' + (result.error || 'Something went wrong.'));
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('❌ Network error. Please try again.');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });
}

function showToast(message) {
    const existing = document.querySelector('.success-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'success-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        background: ${message.includes('✅') ? '#22c55e' : '#ef4444'};
        color: white;
        padding: 12px 24px;
        border-radius: 40px;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        max-width: 90%;
        text-align: center;
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}