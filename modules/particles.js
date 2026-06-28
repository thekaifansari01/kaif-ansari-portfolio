(function() {
    if (window.innerWidth < 969) return;
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initParticles);
    } else {
        initParticles();
    }
    function initParticles() {
        if (typeof tsParticles === 'undefined') return;
        if (document.querySelector('#tsparticles canvas')) return;
        tsParticles.load({
            id: "tsparticles",
            options: {
                fpsLimit: 30,
                particles: {
                    color: {
                        value: ["#ffffff", "#dddddd", "#bbbbbb", "#999999"],
                    },
                    shape: {
                        type: "circle",
                    },
                    size: {
                        value: { min: 1.5, max: 4.5 },
                        animation: {
                            enable: true,
                            speed: 0.8,
                            minimumValue: 0.5,
                            sync: false,
                        },
                    },
                    opacity: {
                        value: { min: 0.2, max: 0.7 },
                        animation: {
                            enable: true,
                            speed: 0.3,
                            minimumValue: 0.1,
                            sync: false,
                        },
                    },
                    move: {
                        direction: "none",
                        enable: true,
                        outModes: { default: "bounce" },
                        random: false,
                        speed: 0.8,
                        straight: false,
                        attract: {
                            enable: true,
                            rotateX: 600,
                            rotateY: 800,
                        },
                    },
                    number: {
                        density: { enable: true, area: 800 },
                        value: 50,
                    },
                    links: {
                        color: { value: "rgba(255,255,255,0.15)" },
                        distance: 150,
                        enable: true,
                        opacity: 0.25,
                        width: 0.8,
                    },
                    twinkle: {
                        particles: {
                            enable: true,
                            frequency: 0.04,
                            opacity: 0.6,
                        },
                    },
                },
                background: {
                    color: "transparent",
                },
                interactivity: {
                    events: {
                        onHover: {
                            enable: true,
                            mode: "grab",
                            parallax: {
                                enable: true,
                                force: 30,
                                smooth: 5,
                            },
                        },
                        onClick: {
                            enable: true,
                            mode: "push",
                        },
                        resize: true,
                    },
                    modes: {
                        grab: {
                            distance: 160,
                            links: {
                                opacity: 0.5,
                                color: "#ffffff",
                            },
                        },
                        push: {
                            quantity: 3,
                        },
                    },
                },
                detectRetina: true,
            },
        });
    }
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            if (window.innerWidth >= 969) {
                if (!document.querySelector('#tsparticles canvas')) initParticles();
            }
        }, 300);
    });
})();