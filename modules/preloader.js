(function () {
    const preloader = document.getElementById('preloader');
    if (!preloader) return;

    try {
        if (sessionStorage.getItem('pl-shown') === '1') {
            preloader.classList.add('fade-out');
            setTimeout(() => preloader.remove(), 700);
            return;
        }
        sessionStorage.setItem('pl-shown', '1');
    } catch (e) {}

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        preloader.classList.add('fade-out');
        setTimeout(() => preloader.remove(), 700);
        return;
    }

    const prevOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';

    const stage    = document.getElementById('pl-stage');
    const grid     = document.getElementById('pl-grid');
    const ambient  = document.getElementById('pl-ambient');
    const signal   = document.getElementById('pl-signal');
    const trail2   = document.getElementById('pl-signal-2');
    const trail3   = document.getElementById('pl-signal-3');
    const tildeEl  = document.getElementById('pl-tilde');
    const nameEl   = document.getElementById('pl-name');

    const nodes = {
        n0: document.getElementById('pl-n0'),
        n1: document.getElementById('pl-n1'),
        n2: document.getElementById('pl-n2'),
        n3: document.getElementById('pl-n3'),
    };

    const rings = {
        n0: document.getElementById('pl-ring0'),
        n1: document.getElementById('pl-ring1'),
        n2: document.getElementById('pl-ring2'),
        n3: document.getElementById('pl-ring3'),
    };

    const edges = {
        e01:    document.getElementById('pl-e01'),
        e12:    document.getElementById('pl-e12'),
        e23:    document.getElementById('pl-e23'),
        e23new: document.getElementById('pl-e23-new'),
        loop:   document.getElementById('pl-e-loop'),
    };

    const coords = {
        n0: [80, 200],
        n1: [160, 200],
        n2: [240, 220],
        n3: [320, 200],
    };

    const timers = [];
    const at = (ms, fn) => timers.push(setTimeout(fn, ms));

    function moveSignal(x, y, duration, easing) {
        duration = duration || 0;
        easing = easing || 'cubic-bezier(0.22, 1, 0.36, 1)';
        const list = [
            { el: signal, delay: 0 },
            { el: trail2, delay: 55 },
            { el: trail3, delay: 110 },
        ];
        list.forEach(({ el, delay }) => {
            if (duration === 0) {
                el.style.transition = 'none';
                el.style.transitionDelay = '0ms';
                el.style.transform = `translate(${x}px, ${y}px)`;
            } else {
                el.style.transition =
                    `transform ${duration}ms ${easing}, opacity 0.25s`;
                el.style.transitionDelay = `${delay}ms`;
                el.style.transform = `translate(${x}px, ${y}px)`;
            }
        });
        if (duration === 0) void signal.getBoundingClientRect();
    }

    function signalOn() {
        signal.classList.add('on');
        trail2.classList.add('on');
        trail3.classList.add('on');
    }

    function signalOff() {
        signal.classList.remove('on');
        trail2.classList.remove('on');
        trail3.classList.remove('on');
    }

    function prepareDraw(edge) {
        const len = edge.getTotalLength();
        edge.style.strokeDasharray  = len;
        edge.style.strokeDashoffset = len;
    }

    function drawIn(edge, duration) {
        duration = duration || 400;
        edge.style.transition =
            `stroke-dashoffset ${duration}ms cubic-bezier(0.22,1,0.36,1), stroke 0.45s, opacity 0.45s`;
        void edge.getBoundingClientRect();
        edge.style.strokeDashoffset = 0;
    }

    function pulseNode(node, ring) {
        node.classList.add('on');
        node.setAttribute('r', 8);
        setTimeout(() => node.setAttribute('r', 5.5), 240);
        if (ring) {
            ring.classList.remove('pulse');
            void ring.getBoundingClientRect();
            ring.classList.add('pulse');
        }
    }

    function typeText(el, text, speed, done) {
        let i = 0;
        const step = () => {
            el.textContent = text.slice(0, i);
            i++;
            if (i <= text.length) setTimeout(step, speed);
            else if (done) done();
        };
        step();
    }

    function init() {
        [edges.e01, edges.e12, edges.e23, edges.loop, edges.e23new]
            .forEach(prepareDraw);
        moveSignal(80, 200, 0);
    }

    function play() {
        init();

        at(80, () => {
            grid.classList.add('on');
            ambient.classList.add('on');
        });

        at(260, () => pulseNode(nodes.n0, rings.n0));

        at(460, () => {
            drawIn(edges.e01, 260);
            at(220, () => pulseNode(nodes.n1, rings.n1));
        });

        at(760, () => {
            drawIn(edges.e12, 260);
            at(220, () => pulseNode(nodes.n2, rings.n2));
        });

        at(1060, () => {
            drawIn(edges.e23, 260);
            at(220, () => pulseNode(nodes.n3, rings.n3));
        });

        at(1440, () => {
            signalOn();
            moveSignal(coords.n0[0], coords.n0[1], 0);
        });

        at(1580, () => {
            edges.e01.classList.add('active');
            nodes.n1.classList.add('hit');
            moveSignal(coords.n1[0], coords.n1[1], 200);
        });

        at(1800, () => {
            edges.e01.classList.remove('active');
            nodes.n1.classList.remove('hit');
            edges.e12.classList.add('active');
            moveSignal(coords.n2[0], coords.n2[1], 200);
        });

        at(2040, () => {
            edges.e12.classList.remove('active');
            nodes.n2.classList.add('flash');
            stage.classList.add('shake');
            signalOff();
            setTimeout(() => stage.classList.remove('shake'), 440);
        });

        at(2480, () => {
            nodes.n2.classList.remove('flash');
            edges.e23.classList.add('fading');
            edges.e23new.classList.add('visible');
            drawIn(edges.e23new, 400);
        });

        at(2940, () => {
            edges.e23new.classList.add('active');
            signalOn();
            moveSignal(coords.n2[0], coords.n2[1], 0);
            at(40, () => moveSignal(coords.n3[0], coords.n3[1], 320));
        });

        at(3300, () => {
            nodes.n3.classList.add('hit');
            edges.e23new.classList.remove('active');
            pulseNode(nodes.n3, rings.n3);
        });

        at(3540, () => {
            nodes.n3.classList.remove('hit');
        });

        at(3600, () => {
            drawIn(edges.loop, 620);
            edges.loop.classList.add('active');
        });

        at(3780, () => {
            moveSignal(coords.n3[0], coords.n3[1], 0);
            at(0,   () => moveSignal(260, 110, 170, 'linear'));
            at(170, () => moveSignal(200, 80,  170, 'linear'));
            at(340, () => moveSignal(140, 110, 170, 'linear'));
            at(510, () => moveSignal(80,  200, 170, 'linear'));
        });

        at(4400, () => {
            edges.loop.classList.remove('active');
            signalOff();
            pulseNode(nodes.n0, rings.n0);
        });

        at(4560, () => {
            typeText(tildeEl, '~/', 90);
            typeText(nameEl, 'kaif', 90);
        });

        at(5500, () => {
            preloader.classList.add('fade-out');
            document.documentElement.style.overflow = prevOverflow;
            setTimeout(() => preloader.remove(), 800);
        });
    }

    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(play);
    } else {
        window.addEventListener('load', play);
    }
})();