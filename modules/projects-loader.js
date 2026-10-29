(function () {
  'use strict';

  var grid = document.getElementById('workGrid');
  if (!grid) return;

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function timeAgo(iso) {
    if (!iso) return '—';
    var ts = Date.parse(iso);
    if (!ts) return '—';
    var diff = Date.now() - ts;
    if (diff < 0) return 'just now';
    var m = Math.floor(diff / 60000);
    if (m < 1) return 'just now';
    if (m < 60) return m + 'm ago';
    var h = Math.floor(m / 60);
    if (h < 24) return h + 'h ago';
    var d = Math.floor(h / 24);
    if (d < 7) return d + 'd ago';
    if (d < 30) return Math.floor(d / 7) + 'w ago';
    return Math.floor(d / 30) + 'mo ago';
  }

  function slugify(s) {
    return String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'project';
  }

  function renderProject(p, index) {
    var featured = !!p.featured;
    var status = p.status || 'shipped';
    var dotClass = status === 'live' ? 'status-dot' : 'status-dot nostroke';
    var idx = String(index + 1).padStart(2, '0');
    var path = p.path || slugify(p.title);
    var metrics = p.metrics || {};

    var brackets = featured
      ? '<span class="work-bracket tl"></span><span class="work-bracket tr"></span><span class="work-bracket bl"></span><span class="work-bracket br"></span>'
      : '';

    var features = '';
    if (featured && Array.isArray(p.features) && p.features.length) {
      features = '<ul class="work-features">' +
        p.features.map(function (f) { return '<li>' + esc(f) + '</li>'; }).join('') +
        '</ul>';
    }

    var stackTags = '';
    if (Array.isArray(p.stack) && p.stack.length) {
      stackTags = p.stack.map(function (s) { return '<span>' + esc(s) + '</span>'; }).join('');
    }

    var metaTags = '';
    if (featured && Array.isArray(p.stack) && p.stack.length) {
      metaTags = p.stack.slice(0, 2).map(function (t) {
        return '<span class="work-tag">' + esc(t) + '</span>';
      }).join('');
    }

    var link = p.github_url || p.live_url || '#';
    var linkAttrs = link !== '#'
      ? 'href="' + esc(link) + '" target="_blank" rel="noopener noreferrer"'
      : 'href="#"';

    var metricsHtml = '';
    if (metrics.stars != null) {
      metricsHtml += '<span class="work-metric"><span class="metric-icon">★</span><span class="metric-val">' + esc(metrics.stars) + '</span></span>';
    }
    if (metrics.forks != null) {
      metricsHtml += '<span class="work-metric"><span class="metric-icon">⑂</span><span class="metric-val">' + esc(metrics.forks) + '</span></span>';
    }
    if (metrics.updated_at) {
      metricsHtml += '<span class="work-metric"><span class="metric-icon">↻</span><span class="metric-val">' + esc(timeAgo(metrics.updated_at)) + '</span></span>';
    }

    var cardClass = 'work-card' + (featured ? ' feature' : '') + ' reveal';

    return '<article class="' + cardClass + '">' +
      brackets +
      '<span class="scanline"></span>' +
      '<span class="work-index">' + idx + '</span>' +
      '<header class="work-card-header">' +
      '<div class="work-dots"><span></span><span></span><span></span></div>' +
      '<span class="work-path"><span class="prompt">$</span>cd ~/projects/' + esc(path) + '</span>' +
      '<span class="work-status ' + esc(status) + '"><span class="' + dotClass + '"></span>' + esc(status) + '</span>' +
      '</header>' +
      '<div class="work-card-body">' +
      '<div class="work-card-meta">' +
      '<span class="work-category">' + esc(p.category || '') + '</span>' +
      metaTags +
      '</div>' +
      '<h3>' + esc(p.title || '') + '</h3>' +
      '<p>' + esc(p.description || '') + '</p>' +
      features +
      '<div class="work-stack">' + stackTags + '</div>' +
      '</div>' +
      '<footer class="work-card-footer">' +
      '<div class="work-metrics">' + metricsHtml + '</div>' +
      '<a ' + linkAttrs + ' class="work-cta" aria-label="Open ' + esc(p.title || 'project') + '">' +
      'open<span class="arrow">→</span>' +
      '</a>' +
      '</footer>' +
      '</article>';
  }

  function initStagger(children) {
    for (var i = 0; i < children.length; i++) {
      children[i].style.setProperty('--stagger-i', i);
      if (!children[i].classList.contains('stagger-item')) {
        children[i].classList.add('stagger-item');
      }
    }
    grid.classList.add('is-staggered');
  }

  async function load() {
    try {
      var res = await fetch('/api/projects', { credentials: 'omit' });
      if (!res.ok) return;
      var data = await res.json();
      if (!data || !data.success || !Array.isArray(data.data) || !data.data.length) return;

      var html = data.data.map(function (p, i) { return renderProject(p, i); }).join('');
      grid.innerHTML = html;

      var children = Array.prototype.slice.call(grid.children);
      initStagger(children);

      if (typeof window.__revealObserve === 'function') {
        children.forEach(function (el) { window.__revealObserve(el); });
      } else {
        children.forEach(function (el) { el.classList.add('revealed'); });
      }
    } catch (e) {
      // keep fallback
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();