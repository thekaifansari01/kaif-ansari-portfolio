// ============================================================
// TOP NAVBAR – Scroll effect & Mobile menu
// ============================================================

const navbar = document.querySelector('.navbar-premium');
const mobileBtn = document.querySelector('.mobile-menu-btn');
const mobilePanel = document.querySelector('.mobile-nav-panel');

// Create mobile panel if not exists (for top navbar hamburger menu)
if (!document.querySelector('.mobile-nav-panel')) {
    const panel = document.createElement('div');
    panel.className = 'mobile-nav-panel';
    const navLinks = document.querySelector('.nav-links-premium');
    if (navLinks) {
        panel.innerHTML = navLinks.innerHTML;
        document.body.appendChild(panel);
    }
}

const mobilePanelElem = document.querySelector('.mobile-nav-panel');

// Top navbar scroll effect (adds shadow on scroll)
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar?.classList.add('scrolled');
    } else {
        navbar?.classList.remove('scrolled');
    }
});

// ============================================================
// ACTIVE NAV LINK – Top navbar + Bottom navbar both
// ============================================================

const sections = document.querySelectorAll('section[id]');

function updateActiveLink() {
    let current = '';
    
    // Find which section is currently in view
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.scrollY >= sectionTop - 300) {
            current = section.getAttribute('id');
        }
    });

    // ----- Update TOP navbar links (desktop) -----
    document.querySelectorAll('.nav-links-premium .nav-link').forEach(link => {
        link.classList.remove('active-nav');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active-nav');
        }
    });

    // ----- Update BOTTOM navbar links (mobile) -----
    document.querySelectorAll('.bottom-nav .nav-item').forEach(link => {
        link.classList.remove('active-nav');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active-nav');
        }
    });
}

// Listen to scroll and run the active link updater
window.addEventListener('scroll', updateActiveLink);
// Run once on load to set initial active state
updateActiveLink();

// ============================================================
// TOP NAVBAR – Hamburger menu toggle
// ============================================================

if (mobileBtn) {
    mobileBtn.addEventListener('click', () => {
        mobileBtn.classList.toggle('active');
        mobilePanelElem?.classList.toggle('active');
    });
}

// Close mobile menu when clicking a link (top navbar)
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        mobileBtn?.classList.remove('active');
        mobilePanelElem?.classList.remove('active');
    });
});

// ============================================================
// BOTTOM NAVBAR – Smooth scroll on click (mobile)
// ============================================================

document.querySelectorAll('.bottom-nav .nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        const target = document.querySelector(item.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ============================================================
// TOUCH RIPPLE EFFECT – for .touch-ripple elements (mobile)
// ============================================================

document.querySelectorAll('.touch-ripple').forEach(el => {
    el.addEventListener('pointerdown', function(e) {
        const rect = this.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        this.style.setProperty('--x', x + '%');
        this.style.setProperty('--y', y + '%');
    });
});

// ============================================================
// (Optional) Close bottom nav active state on route change
// Just a safety net – already handled by updateActiveLink
// ============================================================

console.log('✅ Navbar & Touch Ripple initialized');