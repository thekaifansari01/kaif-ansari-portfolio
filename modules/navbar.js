// modules/navbar.js
(function(){
    const navbar = document.querySelector('.navbar-premium');
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    let mobilePanel = document.querySelector('.mobile-nav-panel');
    const navLinks = document.querySelector('.nav-links-premium');

    if (!mobilePanel && navLinks) {
        const panel = document.createElement('div');
        panel.className = 'mobile-nav-panel';
        panel.innerHTML = navLinks.innerHTML;
        const closeBtn = document.createElement('button');
        closeBtn.className = 'mobile-panel-close';
        closeBtn.innerHTML = '✕';
        panel.prepend(closeBtn);
        document.body.appendChild(panel);
        mobilePanel = panel;
    }

    const panelClose = mobilePanel ? mobilePanel.querySelector('.mobile-panel-close') : null;

    function closeMobileMenu() {
        if (mobileBtn) mobileBtn.classList.remove('active');
        if (mobilePanel) mobilePanel.classList.remove('active');
    }

    function openMobileMenu() {
        if (mobileBtn) mobileBtn.classList.add('active');
        if (mobilePanel) mobilePanel.classList.add('active');
    }

    if (mobileBtn) {
        mobileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (mobilePanel && mobilePanel.classList.contains('active')) {
                closeMobileMenu();
            } else {
                openMobileMenu();
            }
        });
    }

    if (panelClose) {
        panelClose.addEventListener('click', closeMobileMenu);
    }

    document.addEventListener('click', function(e) {
        if (mobilePanel && mobilePanel.classList.contains('active')) {
            if (!mobilePanel.contains(e.target) && !mobileBtn.contains(e.target)) {
                closeMobileMenu();
            }
        }
    });

    document.querySelectorAll('.nav-link, .mobile-nav-panel .nav-link').forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });

    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    const sections = document.querySelectorAll('section[id]');
    function updateActiveLink() {
        let current = '';
        sections.forEach(section => {
            const top = section.offsetTop;
            const height = section.clientHeight;
            if (window.scrollY >= top - 300) {
                current = section.getAttribute('id');
            }
        });
        document.querySelectorAll('.nav-links-premium .nav-link, .mobile-nav-panel .nav-link').forEach(link => {
            link.classList.remove('active-nav');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active-nav');
            }
        });
        document.querySelectorAll('.bottom-nav .nav-item').forEach(item => {
            item.classList.remove('active-nav');
            if (item.getAttribute('href') === '#' + current) {
                item.classList.add('active-nav');
            }
        });
    }
    window.addEventListener('scroll', updateActiveLink);
    updateActiveLink();

    document.querySelectorAll('.bottom-nav .nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    document.querySelectorAll('.touch-ripple').forEach(el => {
        el.addEventListener('pointerdown', function(e) {
            const rect = this.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            this.style.setProperty('--x', x + '%');
            this.style.setProperty('--y', y + '%');
        });
    });
})();