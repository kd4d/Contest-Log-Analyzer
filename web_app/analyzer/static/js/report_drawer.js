/**
 * Report manifest drawer: open/close, filter, and integrate with overlay.
 * - Trigger opens drawer; scrim or close button closes it.
 * - Search filters categories/items by label.
 * - Report links use .report-overlay-link so existing overlay opens them; drawer closes on link click.
 * - data-action="download" triggers the Download All button and closes drawer.
 */
(function() {
    var trigger = document.getElementById('report-drawer-trigger');
    var scrim = document.getElementById('report-drawer-scrim');
    var panel = document.getElementById('report-drawer-panel');
    var closeBtn = document.getElementById('report-drawer-close');
    var searchInput = document.getElementById('report-drawer-search-input');

    function openDrawer() {
        if (!scrim || !panel) return;
        scrim.classList.add('show');
        panel.classList.add('show');
        scrim.setAttribute('aria-hidden', 'false');
        panel.setAttribute('aria-hidden', 'false');
        if (searchInput) {
            searchInput.value = '';
            filterDrawer('');
        }
        document.body.style.overflow = 'hidden';
    }

    function closeDrawer() {
        if (!scrim || !panel) return;
        scrim.classList.remove('show');
        panel.classList.remove('show');
        scrim.setAttribute('aria-hidden', 'true');
        panel.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    function filterDrawer(q) {
        var body = document.getElementById('report-drawer-body');
        if (!body) return;
        q = (q || '').toLowerCase().trim();
        var categories = body.querySelectorAll('.report-drawer-category');
        categories.forEach(function(cat) {
            var catLabel = (cat.getAttribute('data-category-label') || '').toLowerCase();
            var items = cat.querySelectorAll('.report-drawer-item');
            var visibleCount = 0;
            items.forEach(function(item) {
                var itemLabel = (item.getAttribute('data-item-label') || '').toLowerCase();
                var show = !q || catLabel.indexOf(q) !== -1 || itemLabel.indexOf(q) !== -1;
                item.style.display = show ? '' : 'none';
                if (show) visibleCount++;
            });
            cat.style.display = (!q || visibleCount > 0 || catLabel.indexOf(q) !== -1) ? '' : 'none';
        });
    }

    function init() {
        if (!panel) return;

        // Main trigger button (on dashboard)
        if (trigger) {
            trigger.addEventListener('click', function() {
                openDrawer();
            });
        }

        // Overlay trigger button (when viewing a report in overlay)
        var overlayTrigger = document.getElementById('report-overlay-drawer-trigger');
        if (overlayTrigger) {
            overlayTrigger.addEventListener('click', function() {
                openDrawer();
            });
        }

        if (scrim) {
            scrim.addEventListener('click', closeDrawer);
        }
        if (closeBtn) {
            closeBtn.addEventListener('click', closeDrawer);
        }

        if (searchInput) {
            searchInput.addEventListener('input', function() {
                filterDrawer(this.value);
            });
        }

        // Toggle category collapse
        var drawerBody = document.getElementById('report-drawer-body');
        if (drawerBody) {
            drawerBody.addEventListener('click', function(e) {
                var t = e.target && (e.target.closest && e.target.closest('[data-toggle-category]'));
                if (t) {
                    e.preventDefault();
                    var cat = t.closest('.report-drawer-category');
                    if (cat) cat.classList.toggle('collapsed');
                }
            });
        }

        // Report links: close drawer when opening overlay (delegate)
        panel.addEventListener('click', function(e) {
            var link = e.target && e.target.closest && e.target.closest('a');
            if (!link) return;
            if (link.getAttribute('data-action') === 'download') {
                e.preventDefault();
                closeDrawer();
                var downloadBtn = document.getElementById('downloadAllBtn');
                if (downloadBtn) {
                    downloadBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    downloadBtn.focus();
                }
                return;
            }
            if (link.classList.contains('report-overlay-link')) {
                closeDrawer();
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && panel.classList.contains('show')) {
                closeDrawer();
            }
        });

        document.addEventListener('report-overlay-open', function(e) {
            var href = e.detail && e.detail.href;
            if (!href || !panel) return;
            panel.querySelectorAll('a.report-overlay-link').forEach(function(a) {
                var aHref = (a.getAttribute('href') || '').split('?')[0];
                if (aHref === href.split('?')[0]) {
                    a.classList.add('active');
                } else {
                    a.classList.remove('active');
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
