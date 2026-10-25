(function () {
  var popup = document.getElementById('newsletterPopup');
  if (!popup) return;

  var popupCard = popup.querySelector('.nb-popup');
  var closeBtn = document.getElementById('nbPopupClose');
  var form = document.getElementById('newsletterForm');
  var emailInput = document.getElementById('nlEmail');
  var submitBtn = form.querySelector('button[type="submit"]');
  var submitOriginalHTML = submitBtn.innerHTML;
  var popupNote = popup.querySelector('.nb-popup-note');
  var STORAGE_KEY = 'nl-popup-shown';
  var SESSION_KEY = 'nl-popup-session';
  var successPanel = null;
  var isOpen = false;

  try {
    var params = new URLSearchParams(window.location.search);
    var sub = params.get('subscribed');
    if (sub === '1' || sub === '0') {
      setTimeout(function () {
        if (sub === '1') {
          showToast('subscription confirmed ✓', true);
        } else {
          showToast('confirmation link is invalid or expired', false);
        }
      }, 500);
      params.delete('subscribed');
      var qs = params.toString();
      var cleanURL = window.location.pathname + (qs ? '?' + qs : '') + window.location.hash;
      window.history.replaceState({}, '', cleanURL);
    }
  } catch (e) {}

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
    if (isOpen || !canShow()) return;
    isOpen = true;
    resetToForm();
    popup.classList.add('is-open');
    popup.setAttribute('aria-hidden', 'false');
    markShown();
    setTimeout(function () {
      if (emailInput) emailInput.focus();
    }, 400);
  }

  function closePopup() {
    if (!isOpen) return;
    isOpen = false;
    popup.classList.remove('is-open');
    popup.setAttribute('aria-hidden', 'true');
  }

  closeBtn.addEventListener('click', closePopup);

  popup.addEventListener('click', function (e) {
    if (e.target === popup) closePopup();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && isOpen) closePopup();
  });

  var delayTimer = setTimeout(openPopup, 15000);

  var exitTimer = null;
  function onMouseLeave(e) {
    if (e.clientY > 0 || exitTimer) return;
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

  function showSuccess(title, message) {
    if (!successPanel) {
      successPanel = document.createElement('div');
      successPanel.className = 'nb-popup-success';
      popupCard.insertBefore(successPanel, form);
    }
    successPanel.innerHTML =
      '<div class="nb-popup-success-icon">✓</div>' +
      '<h4 class="nb-popup-success-title">' + title + '</h4>' +
      '<p class="nb-popup-success-msg">' + message + '</p>';
    successPanel.classList.add('is-visible');
    form.style.display = 'none';
    if (popupNote) popupNote.style.display = 'none';
  }

  function resetToForm() {
    if (successPanel) {
      successPanel.classList.remove('is-visible');
      successPanel.innerHTML = '';
    }
    form.style.display = '';
    if (popupNote) popupNote.style.display = '';
    form.reset();
    submitBtn.innerHTML = submitOriginalHTML;
    submitBtn.disabled = false;
    emailInput.disabled = false;
    if (typeof turnstile !== 'undefined') {
      try { turnstile.reset(); } catch (e) {}
    }
  }

  function setLoading(on) {
    if (on) {
      submitBtn.innerHTML = 'sending…';
      submitBtn.disabled = true;
      emailInput.disabled = true;
    } else {
      submitBtn.innerHTML = submitOriginalHTML;
      submitBtn.disabled = false;
      emailInput.disabled = false;
    }
  }

  function resetTurnstile() {
    if (typeof turnstile !== 'undefined') {
      try { turnstile.reset(); } catch (e) {}
    }
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    var email = emailInput.value.trim().toLowerCase();

    if (!email) {
      showToast('please enter your email', false);
      emailInput.focus();
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showToast('please enter a valid email address', false);
      emailInput.focus();
      return;
    }

    var tokenInput = form.querySelector('[name="cf-turnstile-response"]');
    var token = tokenInput ? tokenInput.value : '';
    if (!token || token.length < 10) {
      showToast('please complete the captcha first', false);
      return;
    }

    setLoading(true);

    try {
      var res = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, token: token })
      });

      var data = {};
      try { data = await res.json(); } catch (e) {}

      if (res.ok && data.success) {
        var msg = (data.message || '').toLowerCase();
        if (msg.indexOf('already') !== -1) {
          showSuccess(
            "you're already subscribed",
            "You're on the list. Past updates and new drops will land in your inbox."
          );
          showToast('already subscribed', true);
        } else {
          showSuccess(
            'check your email',
            'We sent a confirmation link to ' + email + '. Click it to finish subscribing.'
          );
          showToast('confirmation email sent ✓', true);
        }
        setLoading(false);
        return;
      }

      if (res.status === 429) {
        showToast('too many attempts — try again later', false);
      } else if (res.status === 400) {
        var errMsg = (data.error || '').toLowerCase();
        if (errMsg.indexOf('captcha') !== -1) {
          showToast('captcha failed — please try again', false);
          resetTurnstile();
        } else if (errMsg.indexOf('email') !== -1) {
          showToast('invalid email address', false);
          emailInput.focus();
        } else {
          showToast(data.error || 'request failed', false);
        }
      } else if (res.status >= 500) {
        showToast('server error — please try again', false);
      } else {
        showToast(data.error || 'something went wrong', false);
      }

      setLoading(false);

    } catch (err) {
      showToast('network error — check your connection', false);
      setLoading(false);
    }
  });

  function showToast(msg, ok) {
    var old = document.querySelector('.nb-toast');
    if (old) old.remove();

    var el = document.createElement('div');
    el.className = 'nb-toast';
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
      'font-weight:600',
      'z-index:100001',
      'box-shadow:0 8px 24px rgba(0,0,0,0.25)',
      'max-width:90%',
      'text-align:center',
      'border:2px solid var(--nb-border)'
    ].join(';');

    document.body.appendChild(el);
    setTimeout(function () { el.remove(); }, 3500);
  }
})();