// Initialize AOS
AOS.init({
    duration: 800,
    once: true,
    offset: 100
});

// Theme Management
const themeSwitch = document.querySelector('.theme-switch-track');
const html = document.documentElement;

const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    html.setAttribute('data-theme', savedTheme);
}

themeSwitch.addEventListener('click', () => {
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// Preloader
window.addEventListener('load', () => {
    const preloader = document.querySelector('.preloader');
    setTimeout(() => {
        preloader.classList.add('fade-out');
    }, 500);
});

// Custom Cursor
const cursorFollower = document.querySelector('.cursor-follower');
const cursorDot = document.querySelector('.cursor-dot-premium');

document.addEventListener('mousemove', (e) => {
    cursorFollower.style.transform = `translate(${e.clientX - 20}px, ${e.clientY - 20}px)`;
    cursorDot.style.transform = `translate(${e.clientX - 3}px, ${e.clientY - 3}px)`;
});

// Hover effect for clickable elements
const clickables = document.querySelectorAll('a, button, .work-card, .skill-category');
clickables.forEach(el => {
    el.addEventListener('mouseenter', () => {
        cursorFollower.style.transform = `scale(1.5)`;
        cursorFollower.style.opacity = '0.3';
    });
    el.addEventListener('mouseleave', () => {
        cursorFollower.style.transform = `scale(1)`;
        cursorFollower.style.opacity = '0.6';
    });
});

// Navbar Scroll Effect
const navbar = document.querySelector('.navbar-premium');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Active Nav Link on Scroll
const sections = document.querySelectorAll('section[id]');
window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (scrollY >= sectionTop - 300) {
            current = section.getAttribute('id');
        }
    });
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active-nav');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active-nav');
        }
    });
});

// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Counter Animation
const counters = document.querySelectorAll('.stat-number');
const speed = 200;

const animateCounter = (counter) => {
    const target = parseInt(counter.getAttribute('data-target'));
    let count = 0;
    const increment = target / speed;
    
    const updateCount = () => {
        if (count < target) {
            count += increment;
            counter.innerText = Math.ceil(count);
            setTimeout(updateCount, 20);
        } else {
            counter.innerText = target;
        }
    };
    updateCount();
};

// Trigger counters when in viewport
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounter(entry.target);
            counterObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

counters.forEach(counter => {
    counterObserver.observe(counter);
});

// Contact Form
const contactForm = document.getElementById('premiumContactForm');

contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    // Show success message
    const toast = document.createElement('div');
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
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
    
    contactForm.reset();
});

// Work Card Hover 3D Effect
const workCards = document.querySelectorAll('.work-card');
workCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
    });
});

// Mobile Menu
const mobileBtn = document.querySelector('.mobile-menu-btn');
const navLinks = document.querySelector('.nav-links-premium');

if (mobileBtn) {
    mobileBtn.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        mobileBtn.classList.toggle('active');
    });
}

// Parallax effect on hero
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero-premium');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
});

// Animate skill bars on scroll
const skillObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const fills = entry.target.querySelectorAll('.skill-fill');
            fills.forEach(fill => {
                const width = fill.style.width;
                fill.style.width = '0';
                setTimeout(() => {
                    fill.style.width = width;
                }, 100);
            });
        }
    });
}, { threshold: 0.3 });

document.querySelectorAll('.skill-category').forEach(category => {
    skillObserver.observe(category);
});

// Dynamic year in footer
const yearSpan = document.querySelector('.footer-copyright p');
if (yearSpan) {
    yearSpan.innerHTML = yearSpan.innerHTML.replace('2024', new Date().getFullYear());
}