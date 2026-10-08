(function () {
    var form = document.getElementById('premiumContactForm');
    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        var tokenInput = document.querySelector('[name="cf-turnstile-response"]');
        var token = tokenInput ? tokenInput.value : null;
        if (!token || token.length < 10) {
            toast('please complete the captcha', false);
            return;
        }

        var name = document.getElementById('premiumName').value;
        var email = document.getElementById('premiumEmail').value;
        var message = document.getElementById('premiumMessage').value;
        var submitBtn = form.querySelector('button[type="submit"]');
        var original = submitBtn.innerHTML;

        submitBtn.innerHTML = 'sending…';
        submitBtn.disabled = true;

        try {
            var resp = await fetch('/api/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name, email: email, message: message, token: token })
            });
            var data = await resp.json();
            if (resp.ok && data.success) {
                toast('message sent ✓', true);
                form.reset();
                if (typeof turnstile !== 'undefined') turnstile.reset();
            } else {
                toast(data.error || 'something broke', false);
            }
        } catch (err) {
            toast('network error', false);
        } finally {
            submitBtn.innerHTML = original;
            submitBtn.disabled = false;
        }
    });

    function toast(msg, ok) {
        var old = document.querySelector('.toast');
        if (old) old.remove();

        var el = document.createElement('div');
        el.className = 'toast';
        el.textContent = '$ ' + msg;
        el.style.cssText = [
            'position:fixed',
            'bottom:32px',
            'left:50%',
            'transform:translateX(-50%)',
            'background:' + (ok ? 'var(--accent)' : 'var(--error)'),
            'color:' + (ok ? 'var(--accent-ink)' : '#ffffff'),
            'padding:10px 18px',
            'border-radius:4px',
            'font-family:var(--font-mono)',
            'font-size:13px',
            'z-index:10000',
            'box-shadow:0 8px 24px rgba(0,0,0,0.2)',
            'max-width:90%',
            'text-align:center'
        ].join(';');

        document.body.appendChild(el);
        setTimeout(function () { el.remove(); }, 3500);
    }
})();