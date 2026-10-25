(function () {
  var popup = document.getElementById('newsletterPopup');
  if (!popup) return;

  var closeBtn = document.getElementById('nbPopupClose');
  var form = document.getElementById('newsletterForm');
  var STORAGE_KEY = 'nl-popup-shown';
  var SESSION_KEY = 'nl-popup-session';

  function canShow() {
    try {
      if (sessionStorage.getItem(SESSION_KEY) === '1') return false;
      var last = localStorage.getItem(STORAGE_KEY);
      if (last && Date.now() - parseInt(last, 10) < 7 * 24 * 60 * 60 * 1000) return false;
    } catch (e) {}
    return true;
  }

  function markShown() {
    try {
      sessionStorage.setItem(SESSION_KEY, '1');
      localStorage.setItem(STORAGE_KEY, String(Date.now()));
    } catch (e) {}
  }

  function openPopup() {
    if (!canShow()) return;
    popup.classList.add('is-open');
    popup.setAttribute('aria-hidden', 'false');
    markShown();
  }

  function closePopup() {
    popup.classList.remove('is-open');
    popup.setAttribute('aria-hidden', 'true');
  }

  closeBtn.addEventListener('click', closePopup);

  popup.addEventListener('click', function (e) {
    if (e.target === popup) closePopup();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && popup.classList.contains('is-open')) closePopup();
  });

  var exitTimer = null;
  var delayTimer = setTimeout(openPopup, 15000);

  function onMouseLeave(e) {
    if (e.clientY > 0) return;
    if (exitTimer) return;
    exitTimer = setTimeout(function () {
      openPopup();
      exitTimer = null;
    }, 300);
  }

  if (!window.matchMedia('(hover: none)').matches) {
    document.addEventListener('mouseleave', onMouseLeave);
  }

  var lastY = window.scrollY;
  window.addEventListener('scroll', function () {
    if (window.scrollY < lastY - 80 && window.scrollY > 200) {
      clearTimeout(delayTimer);
      openPopup();
    }
    lastY = window.scrollY;
  }, { passive: true });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    var email = document.getElementById('nlEmail').value.trim();
    var tokenInput = form.querySelector('[name="cf-turnstile-response"]');
    var token = tokenInput ? tokenInput.value : '';

    if (!email || !email.includes('@')) {
      toast('valid email dalo', false);
      return;
    }
    if (!token) {
      toast('captcha complete karo', false);
      return;
    }

    var btn = form.querySelector('button[type="submit"]');
    var original = btn.innerHTML;
    btn.innerHTML = 'sending…';
    btn.disabled = true;

    try {
      var res = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, token: token })
      });
      var data = await res.json();

      if (res.ok && data.success) {
        toast('confirmation email bheja ✓', true);
        form.reset();
        if (typeof turnstile !== 'undefined') turnstile.reset();
        setTimeout(closePopup, 1200);
      } else {
        toast(data.error || 'kuch gadbad hai', false);
      }
    } catch (err) {
      toast('network error', false);
    } finally {
      btn.innerHTML = original;
      btn.disabled = false;
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
      'color:' + (ok ? 'var(--accent-ink)' : '#fff'),
      'padding:10px 18px',
      'border-radius:4px',
      'font-family:var(--font-mono)',
      'font-size:13px',
      'z-index:100001',
      'box-shadow:0 8px 24px rgba(0,0,0,0.2)'
    ].join(';');
    document.body.appendChild(el);
    setTimeout(function () { el.remove(); }, 3500);
  }
})();