// modules/contact-form.js (unchanged, but we'll output as is to avoid changes; however we can keep it)
(function(){
    const form = document.getElementById('premiumContactForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const tokenInput = document.querySelector('[name="cf-turnstile-response"]');
        const token = tokenInput ? tokenInput.value : null;
        if (!token || token.length < 10) {
            showToast('⚠️ Please complete the CAPTCHA verification first.');
            return;
        }

        const name = document.getElementById('premiumName').value;
        const email = document.getElementById('premiumEmail').value;
        const message = document.getElementById('premiumMessage').value;
        const submitBtn = form.querySelector('button[type="submit"]');
        const original = submitBtn.innerHTML;
        submitBtn.innerHTML = '⏳ Sending...';
        submitBtn.disabled = true;

        try {
            const resp = await fetch('/api/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, message, token })
            });
            const data = await resp.json();
            if (resp.ok && data.success) {
                showToast('✅ ' + (data.message || 'Message sent!'));
                form.reset();
                if (typeof turnstile !== 'undefined') turnstile.reset();
            } else {
                showToast('❌ ' + (data.error || 'Something went wrong.'));
            }
        } catch (err) {
            console.error(err);
            showToast('❌ Network error. Please try again.');
        } finally {
            submitBtn.innerHTML = original;
            submitBtn.disabled = false;
        }
    });

    function showToast(msg) {
        const old = document.querySelector('.success-toast');
        if (old) old.remove();
        const toast = document.createElement('div');
        toast.className = 'success-toast';
        toast.textContent = msg;
        const isSuccess = msg.includes('✅');
        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: ${isSuccess ? '#22c55e' : '#ef4444'};
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
})();