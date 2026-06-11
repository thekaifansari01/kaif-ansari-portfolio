const navbar = document.querySelector('.navbar-premium');
const mobileBtn = document.querySelector('.mobile-menu-btn');
const mobilePanel = document.querySelector('.mobile-nav-panel');

// Create mobile panel if not exists
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

// Scroll effect
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar?.classList.add('scrolled');
    } else {
        navbar?.classList.remove('scrolled');
    }
});

// Active nav link highlighting (both desktop + mobile)
const sections = document.querySelectorAll('section[id]');
function updateActiveLink() {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.scrollY >= sectionTop - 300) {
            current = section.getAttribute('id');
        }
    });
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active-nav');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active-nav');
        }
    });
}

window.addEventListener('scroll', updateActiveLink);
updateActiveLink();

// Mobile menu toggle
if (mobileBtn) {
    mobileBtn.addEventListener('click', () => {
        mobileBtn.classList.toggle('active');
        mobilePanelElem?.classList.toggle('active');
    });
}

// Close mobile menu when clicking a link
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        mobileBtn?.classList.remove('active');
        mobilePanelElem?.classList.remove('active');
    });
});