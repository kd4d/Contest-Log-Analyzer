/**
 * Full-screen in-place report overlay.
 * Binds clicks on .report-overlay-link: fetches .txt via AJAX (format=text) or loads HTML in iframe.
 * Does not open new tabs.
 */
(function() {
    function getPathname(href) {
        try {
            return new URL(href, window.location.origin).pathname;
        } catch (_) {
            return href.split('?')[0] || '';
        }
    }

    function buildTextUrl(href) {
        try {
            var u = new URL(href, window.location.origin);
            u.searchParams.set('format', 'text');
            return u.toString();
        } catch (_) {
            return href + (href.indexOf('?') >= 0 ? '&' : '?') + 'format=text';
        }
    }

    function isTextReport(href) {
        var path = getPathname(href);
        return path.length > 0 && path.toLowerCase().endsWith('.txt');
    }

    function reportTitle(link) {
        var title = link.getAttribute('title');
        if (title) return title;
        var text = (link.textContent || '').trim();
        if (text) return text.replace(/\s+/g, ' ');
        var path = getPathname(link.getAttribute('href') || '');
        return path ? path.split('/').pop() : 'Report';
    }

    function showOverlay(options) {
        var overlay = document.getElementById('report-overlay');
        var titleEl = document.getElementById('report-overlay-title');
        var preEl = document.getElementById('report-overlay-pre');
        var iframeEl = document.getElementById('report-overlay-iframe');
        if (!overlay || !titleEl || !preEl || !iframeEl) return;

        if (options.title) titleEl.textContent = options.title;
        preEl.style.display = 'none';
        preEl.textContent = '';
        iframeEl.style.display = 'none';
        iframeEl.src = '';

        if (options.isText) {
            preEl.textContent = options.content || 'Loading…';
            preEl.style.display = 'block';
        } else {
            iframeEl.src = options.url || '';
            iframeEl.style.display = 'block';
        }

        overlay.classList.add('show');
        overlay.setAttribute('aria-hidden', 'false');
    }

    function hideOverlay() {
        var overlay = document.getElementById('report-overlay');
        var preEl = document.getElementById('report-overlay-pre');
        var iframeEl = document.getElementById('report-overlay-iframe');
        if (overlay) {
            overlay.classList.remove('show');
            overlay.setAttribute('aria-hidden', 'true');
        }
        if (preEl) {
            preEl.textContent = '';
            preEl.style.display = 'none';
        }
        if (iframeEl) {
            iframeEl.src = '';
            iframeEl.style.display = 'none';
        }
    }

    function openInOverlay(link) {
        var href = (link.getAttribute('href') || '').trim();
        if (!href || href === '#') return;
        var title = reportTitle(link);

        try {
            document.dispatchEvent(new CustomEvent('report-overlay-open', { detail: { href: href } }));
        } catch (e) {}

        if (isTextReport(href)) {
            var textUrl = buildTextUrl(href);
            showOverlay({ title: title, isText: true, content: 'Loading…' });
            fetch(textUrl)
                .then(function(r) {
                    if (!r.ok) throw new Error('HTTP ' + r.status);
                    return r.text();
                })
                .then(function(text) {
                    var preEl = document.getElementById('report-overlay-pre');
                    if (preEl) preEl.textContent = text;
                })
                .catch(function(err) {
                    var preEl = document.getElementById('report-overlay-pre');
                    if (preEl) preEl.textContent = 'Error loading report: ' + (err.message || 'Unknown error');
                });
        } else {
            showOverlay({ title: title, isText: false, url: href });
        }
    }

    function init() {
        document.addEventListener('click', function(e) {
            var link = e.target && e.target.closest && e.target.closest('a.report-overlay-link');
            if (!link) return;
            e.preventDefault();
            openInOverlay(link);
        });

        var backBtn = document.getElementById('report-overlay-back');
        if (backBtn) {
            backBtn.addEventListener('click', hideOverlay);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
