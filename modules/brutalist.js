(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var cursorLabel = document.getElementById('cursorLabel');
  var isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

  if (cursorLabel && !reduceMotion && !isTouch) {
    var currentTarget = null;
    var mx = 0;
    var my = 0;
    var moveRaf = null;

    var interactiveSelector = 'a, button, input, textarea, [data-cursor-label], .work-card, .stack-category, .form-field';

    var detectLabel = function (el) {
      if (!el) return null;

      var explicit = el.getAttribute && el.getAttribute('data-cursor-label');
      if (explicit) return explicit;

      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') return 'type';

      if (el.classList.contains('nav-resume')) return 'resume';
      if (el.classList.contains('work-cta')) return 'open';
      if (el.classList.contains('work-card')) return 'explore';
      if (el.classList.contains('stack-category')) return 'skills';
      if (el.classList.contains('social-link')) return 'visit';
      if (el.classList.contains('theme-toggle')) return 'theme';
      if (el.classList.contains('nb-popup-close')) return 'close';

      if (el.tagName === 'BUTTON') {
        var btnText = (el.innerText || el.textContent || '').trim().split(/\s+/)[0];
        return btnText ? btnText.toLowerCase().slice(0, 14) : 'click';
      }

      if (el.classList.contains('btn-primary') || el.classList.contains('btn-ghost')) {
        var ctaText = (el.innerText || el.textContent || '').trim().split(/\s+/)[0];
        return ctaText ? ctaText.toLowerCase().slice(0, 14) : 'click';
      }

      if (el.tagName === 'A') {
        var href = el.getAttribute('href') || '';
        if (href.indexOf('mailto:') === 0) return 'email';
        if (href.indexOf('tel:') === 0) return 'call';
        if (href.charAt(0) === '#') {
          var section = href.slice(1);
          return section || 'home';
        }
        if (el.getAttribute('target') === '_blank') return 'visit';
        return 'open';
      }

      return null;
    };

    var showLabel = function (text) {
      cursorLabel.textContent = text;
      cursorLabel.classList.add('is-visible');
    };

    var hideLabel = function () {
      cursorLabel.classList.remove('is-visible');
      currentTarget = null;
    };

    document.addEventListener('mouseover', function (e) {
      var target = e.target.closest ? e.target.closest(interactiveSelector) : null;
      if (!target || target === currentTarget) return;

      var label = detectLabel(target);
      if (!label) {
        hideLabel();
        return;
      }

      currentTarget = target;
      showLabel(label);
    });

    document.addEventListener('mouseout', function (e) {
      var from = e.target.closest ? e.target.closest(interactiveSelector) : null;
      if (!from || from !== currentTarget) return;

      var to = e.relatedTarget && e.relatedTarget.closest ? e.relatedTarget.closest(interactiveSelector) : null;
      if (to === from) return;
      if (to) return;

      hideLabel();
    });

    window.addEventListener('mousemove', function (e) {
      mx = e.clientX;
      my = e.clientY;
      if (!moveRaf) {
        moveRaf = requestAnimationFrame(function () {
          cursorLabel.style.left = mx + 'px';
          cursorLabel.style.top = my + 'px';
          moveRaf = null;
        });
      }
    }, { passive: true });

    window.addEventListener('scroll', function () {
      if (currentTarget) hideLabel();
    }, { passive: true });
  }

  var staggerParents = document.querySelectorAll('[data-stagger]');
  staggerParents.forEach(function (parent) {
    var children = Array.prototype.slice.call(parent.children);
    var hasRevealChildren = children.some(function (c) {
      return c.classList.contains('reveal');
    });

    children.forEach(function (child, i) {
      child.style.setProperty('--stagger-i', i);
    });

    if (hasRevealChildren) return;

    children.forEach(function (child) {
      child.classList.add('stagger-item');
    });

    if (reduceMotion) {
      parent.classList.add('is-staggered');
      return;
    }

    if (typeof IntersectionObserver !== 'undefined') {
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          parent.classList.add('is-staggered');
          obs.disconnect();
        });
      }, { threshold: 0.15 });
      obs.observe(parent);
    } else {
      parent.classList.add('is-staggered');
    }
  });

  if (!reduceMotion && typeof IntersectionObserver !== 'undefined') {
    var glitchTargets = document.querySelectorAll('.section-header h2');
    var glitchObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        el.classList.add('is-glitched');
        glitchObs.unobserve(el);
        setTimeout(function () { el.classList.remove('is-glitched'); }, 500);
      });
    }, { threshold: 0.4 });
    glitchTargets.forEach(function (t) { glitchObs.observe(t); });
  }

  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      var invalids = form.querySelectorAll(':invalid');
      invalids.forEach(function (field) {
        var wrapper = field.closest('.form-field, .nb-popup-field');
        if (!wrapper) return;
        wrapper.classList.remove('has-error');
        void wrapper.offsetWidth;
        wrapper.classList.add('has-error');
        setTimeout(function () { wrapper.classList.remove('has-error'); }, 600);
      });
    });
  });

  var popupOverlay = document.getElementById('newsletterPopup');
  if (popupOverlay && typeof MutationObserver !== 'undefined') {
    var popupObs = new MutationObserver(function () {
      if (popupOverlay.getAttribute('aria-hidden') !== 'false') return;
      var popup = popupOverlay.querySelector('.nb-popup');
      if (!popup) return;
      popup.classList.remove('is-stamping');
      void popup.offsetWidth;
      popup.classList.add('is-stamping');
    });
    popupObs.observe(popupOverlay, { attributes: true, attributeFilter: ['aria-hidden'] });
  }

  if (!reduceMotion) {
    var canvas = document.getElementById('burstCanvas');
    if (canvas && canvas.getContext) {
      var ctx = canvas.getContext('2d');
      var particles = [];
      var burstRaf = null;

      var resizeCanvas = function () {
        canvas.width = window.innerWidth * (window.devicePixelRatio || 1);
        canvas.height = window.innerHeight * (window.devicePixelRatio || 1);
        canvas.style.width = window.innerWidth + 'px';
        canvas.style.height = window.innerHeight + 'px';
        ctx.setTransform(window.devicePixelRatio || 1, 0, 0, window.devicePixelRatio || 1, 0, 0);
      };
      resizeCanvas();
      window.addEventListener('resize', resizeCanvas, { passive: true });

      var renderBurst = function () {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles = particles.filter(function (p) { return p.life > 0; });

        particles.forEach(function (p) {
          p.x += p.vx;
          p.y += p.vy;
          p.vy += 0.4;
          p.vx *= 0.98;
          p.life -= 1;
          ctx.globalAlpha = Math.max(0, p.life / p.maxLife);
          ctx.fillStyle = p.color;
          ctx.fillRect(Math.round(p.x), Math.round(p.y), p.size, p.size);
        });

        ctx.globalAlpha = 1;

        if (particles.length) {
          burstRaf = requestAnimationFrame(renderBurst);
        } else {
          burstRaf = null;
        }
      };

      var spawnBurst = function (e) {
        var styles = getComputedStyle(document.documentElement);
        var accent = (styles.getPropertyValue('--accent-symbol') || '').trim() || '#ff5c00';
        var ink = '#0a0a0a';
        var colors = [accent, ink, accent];
        var count = 12;
        var originX = e.clientX;
        var originY = e.clientY;

        for (var i = 0; i < count; i++) {
          var angle = (Math.PI * 2 / count) * i + (Math.random() - 0.5) * 0.4;
          var speed = 4 + Math.random() * 4;
          particles.push({
            x: originX,
            y: originY,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed - 2.5,
            size: 6,
            life: 24,
            maxLife: 24,
            color: colors[i % colors.length]
          });
        }

        if (!burstRaf) burstRaf = requestAnimationFrame(renderBurst);
      };

      var burstTargets = document.querySelectorAll('.btn-primary, .btn-ghost, .work-cta, .nav-resume, button[type="submit"], .social-link');
      burstTargets.forEach(function (el) {
        el.addEventListener('click', spawnBurst);
      });
    }
  }

})();