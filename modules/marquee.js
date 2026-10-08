(function () {
    var timeEl = document.getElementById('marqueeTime');
    var uptimeEl = document.getElementById('marqueeUptime');
    var marquee = document.getElementById('marquee');

    function pad(n) {
        return n < 10 ? '0' + n : '' + n;
    }

    function updateTime() {
        if (!timeEl) return;
        var now = new Date();
        var ist = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + (5.5 * 3600000));
        timeEl.textContent = pad(ist.getHours()) + ':' + pad(ist.getMinutes()) + ':' + pad(ist.getSeconds());
    }

    var sessionStart = Date.now();

    function updateUptime() {
        if (!uptimeEl) return;
        var elapsed = Math.floor((Date.now() - sessionStart) / 1000);
        var h = Math.floor(elapsed / 3600);
        var m = Math.floor((elapsed % 3600) / 60);
        var s = elapsed % 60;
        uptimeEl.textContent = pad(h) + ':' + pad(m) + ':' + pad(s);
    }

    updateTime();
    updateUptime();
    setInterval(updateTime, 1000);
    setInterval(updateUptime, 1000);

    if (!marquee) return;

    var lastY = window.scrollY;
    var lastTime = Date.now();
    var baseSpeed = 42;
    var currentSpeed = baseSpeed;
    var raf;

    function applySpeed() {
        marquee.style.setProperty('--marquee-speed', currentSpeed + 's');
    }

    function onScroll() {
        if (raf) return;
        raf = requestAnimationFrame(function () {
            var now = Date.now();
            var y = window.scrollY;
            var dy = Math.abs(y - lastY);
            var dt = Math.max(1, now - lastTime);
            var velocity = dy / dt;

            var target = baseSpeed - Math.min(velocity * 12, 22);
            if (target < 18) target = 18;

            currentSpeed += (target - currentSpeed) * 0.18;
            applySpeed();

            lastY = y;
            lastTime = now;
            raf = null;
        });
    }

    function relax() {
        if (Math.abs(currentSpeed - baseSpeed) < 0.2) return;
        currentSpeed += (baseSpeed - currentSpeed) * 0.05;
        applySpeed();
        requestAnimationFrame(relax);
    }

    window.addEventListener('scroll', function () {
        onScroll();
        relax();
    }, { passive: true });

    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            marquee.style.setProperty('--marquee-speed', '999s');
        } else {
            applySpeed();
        }
    });
})();