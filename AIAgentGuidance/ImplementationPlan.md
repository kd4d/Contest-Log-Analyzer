# Implementation Plan - Dashboard Stabilization (Golden Master)
**Version:** 2.0.1
**Target:** 0.148.0-Beta

## Task: Dashboard Template Reset
This plan performs a **Full File Overwrite** of `qso_dashboard.html`. This action addresses two critical issues identified in the analysis:
1.  **Template Syntax Error:** Resolves the "missing endif" crash by providing a verified, balanced template structure.
2.  **Layout Instability:** Implements "Strategy B" (Hard Deck) by hardcoding the iframe height to `900px` via CSS and **deleting the conflicting Javascript auto-resizer**. This eliminates the race condition causing vertical scrollbars.

**Note:** The Builder verified that `chart_qso_breakdown.py` was successfully updated to `0.147.0-Beta` in the previous cycle (generation order swapped). Therefore, no further changes are required for the Python reports; the fix depends entirely on the Dashboard container behaving correctly.

## 1. File: web_app/analyzer/templates/analyzer/qso_dashboard.html
**Action:** Full File Overwrite.
**Reason:** To restore valid syntax, enforce the "Hard Deck" layout strategy (Fixed Height), and retain the necessary dropdown navigation logic while removing the unstable resize logic.

### Full Content
__CODE_BLOCK__ html
{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container-fluid py-4">
    <div class="row mb-3">
        <div class="col-12 d-flex justify-content-end">
            <a href="{% url 'dashboard_view' session_id %}" class="btn btn-outline-secondary">
                <i class="bi bi-arrow-left me-1"></i>Back to Main Dashboard
            </a>
        </div>
    </div>
    <style>
        .nav-tabs .nav-link {
            color: #495057;
        }
        .nav-tabs .nav-link.active {
            font-weight: bold;
            color: #0d6efd;
        }
        .stat-card-value {
            font-size: 2rem;
            font-weight: 700;
        }
        .chart-container {
            position: relative;
            margin: auto;
            height: 300px;
        }
        .empty-state {
            padding: 4rem 2rem;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            text-align: center;
            margin-bottom: 2rem;
        }
        /* Hard Deck Strategy: Fixed height to prevent async thrashing */
        .viewport-frame {
            width: 100%;
            height: 900px;
            border: none;
            background-color: #fff;
        }
    </style>

    <div class="row mb-4">
        <div class="col-12">
            <div class="card shadow-sm">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="bi bi-speedometer2 me-2"></i>Global Context</h5>
                    {% if global_qso_rate_file %}
                    <a href="{% url 'view_report' session_id global_qso_rate_file %}?source=qso" target="_blank" class="btn btn-sm btn-light">
                        <i class="bi bi-box-arrow-up-right"></i>
                    </a>
                    {% endif %}
                </div>
                <div class="card-body p-0">
                    {% if global_qso_rate_file %}
                    <iframe src="{% url 'view_report' session_id global_qso_rate_file %}?chromeless=1" class="viewport-frame"></iframe>
                    {% else %}
                    <div class="d-flex align-items-center justify-content-center h-100 bg-light text-muted" style="min-height: 200px;">
                        <div class="text-center">
                            <i class="bi bi-exclamation-circle display-4 mb-3"></i>
                            <p>Global Rate Plot Not Available</p>
                        </div>
                    </div>
                {% endif %}
                </div>
            </div>
        </div>
    </div>

    <ul class="nav nav-tabs mb-3" id="qsoTabs" role="tablist">
        {% if not is_solo %}
        <li class="nav-item" role="presentation">
            <button class="nav-link active" id="strategy-tab" data-bs-toggle="tab" data-bs-target="#strategy" type="button" role="tab">
                <i class="bi bi-chess me-2"></i>Pairwise Strategy
            </button>
        </li>
        {% endif %}
        <li class="nav-item" role="presentation">
            <button class="nav-link" id="cumul-tab" data-bs-toggle="tab" data-bs-target="#cumul" type="button" role="tab">
                <i class="bi bi-graph-up-arrow me-2"></i>QSOs by Band
            </button>
        </li>
        <li class="nav-item" role="presentation">
            <button class="nav-link {% if is_solo %}active{% endif %}" id="rates-tab" data-bs-toggle="tab" data-bs-target="#rates" type="button" role="tab">
                <i class="bi bi-table me-2"></i>Rate Detail
            </button>
        </li>
        <li class="nav-item" role="presentation">
            <button class="nav-link" id="points-tab" data-bs-toggle="tab" data-bs-target="#points" type="button" role="tab">
                <i class="bi bi-geo-alt me-2"></i>Points & Bands
            </button>
        </li>
    </ul>

    <div class="tab-content" id="qsoTabsContent">
        
        {% if not is_solo %}
        <div class="tab-pane fade show active" id="strategy" role="tabpanel">
            <div class="input-group mb-3 w-auto">
                <label class="input-group-text" for="strategySelect"><i class="bi bi-people me-2"></i>Select Matchup:</label>
                <select class="form-select" id="strategySelect">
                {% for m in matchups %}
                    <option value="{{ forloop.counter }}"
                            data-breakdown="{% url 'view_report' session_id m.qso_breakdown_file %}?chromeless=1"
                        {% for band, path in m.diff_paths.items %}
                        data-diff-{{ band }}="{% url 'view_report' session_id path %}?chromeless=1"
                        {% endfor %}
                            data-full-breakdown="{% url 'view_report' session_id m.qso_breakdown_file %}?source=qso">{{ m.label }}</option>
                {% endfor %}
                </select>
            </div>

            <div class="row">
                <div class="col-lg-6 mb-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span>Strategy Breakdown (Uniques)</span>
                            <a id="link-breakdown" href="#" target="_blank" class="btn btn-xs btn-link text-muted"><i class="bi bi-box-arrow-up-right"></i></a>
                        </div>
                        <div class="card-body p-0">
                            <iframe id="frame-breakdown" src="" class="viewport-frame"></iframe>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <div class="d-flex align-items-center">
                                <span class="me-2">Rate Differential</span>
                                <div class="btn-group btn-group-sm" role="group">
                                    <button type="button" class="btn btn-outline-secondary diff-band-btn" data-band="160">160</button>
                                    <button type="button" class="btn btn-outline-secondary diff-band-btn" data-band="80">80</button>
                                    <button type="button" class="btn btn-outline-secondary diff-band-btn" data-band="40">40</button>
                                    <button type="button" class="btn btn-outline-secondary diff-band-btn" data-band="20">20</button>
                                    <button type="button" class="btn btn-outline-secondary diff-band-btn" data-band="15">15</button>
                                    <button type="button" class="btn btn-outline-secondary diff-band-btn" data-band="10">10</button>
                                    <button type="button" class="btn btn-outline-secondary diff-band-btn active" data-band="all">All</button>
                                </div>
                            </div>
                            <a id="link-diff" href="#" target="_blank" class="btn btn-xs btn-link text-muted"><i class="bi bi-box-arrow-up-right"></i></a>
                        </div>
                        <div class="card-body p-0">
                            <iframe id="frame-diff" src="" class="viewport-frame"></iframe>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <div class="tab-pane fade" id="cumul" role="tabpanel">
            <div class="input-group mb-3 w-auto">
                <label class="input-group-text" for="cumulSelect"><i class="bi bi-filter me-2"></i>Select Band:</label>
                <select class="form-select" id="cumulSelect">
                {% for p in qso_band_plots %}
                    <option value="{{ p.label }}"
                            data-src="{% url 'view_report' session_id p.file %}?chromeless=1"
                            data-full-src="{% url 'view_report' session_id p.file %}?source=qso"
                            {% if p.active %}selected{% endif %}>{{ p.label }}</option>
                {% endfor %}
                </select>
            </div>
            <div class="row">
                <div class="col-12 mb-4">
                    <div class="card shadow-sm">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span>Cumulative QSO Rates (By Band)</span>
                            <a id="link-qso-rates" href="#" target="_blank" class="btn btn-xs btn-link text-muted"><i class="bi bi-box-arrow-up-right"></i></a>
                        </div>
                        <div class="card-body p-0">
                             <iframe id="frame-qso-rates" src="" class="viewport-frame"></iframe>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="tab-pane fade {% if is_solo %}show active{% endif %}" id="rates" role="tabpanel">
            <div class="input-group mb-3 w-auto">
                <label class="input-group-text" for="ratesSelect"><i class="bi bi-journal-text me-2"></i>Select Log:</label>
                <select class="form-select" id="ratesSelect">
                {% if rate_sheet_comparison %}
                    <option value="comparison" selected
                            data-src="{% url 'view_report' session_id rate_sheet_comparison %}?chromeless=1"
                            data-full-src="{% url 'view_report' session_id rate_sheet_comparison %}?source=qso">Comparison (All Logs)</option>
                {% endif %}
                {% for call in callsigns %}
                    <option value="{{ call }}"
                            data-src="{% url 'view_report' session_id report_base|add:'/text/rate_sheet_'|add:call|add:'.txt' %}?chromeless=1"
                            data-full-src="{% url 'view_report' session_id report_base|add:'/text/rate_sheet_'|add:call|add:'.txt' %}?source=qso"
                            {% if is_solo and forloop.first %}selected{% endif %}>{{ call }}</option>
                {% endfor %}
                </select>
            </div>
            <div class="card shadow-sm">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span>Rate Detail</span>
                    <a id="link-rates" href="#" target="_blank" class="btn btn-xs btn-link text-muted"><i class="bi bi-box-arrow-up-right"></i></a>
                </div>
                <div class="card-body p-0">
                    <iframe id="frame-rates" src="" class="viewport-frame"></iframe>
                </div>
            </div>
        </div>

        <div class="tab-pane fade" id="points" role="tabpanel">
            <div class="input-group mb-3 w-auto">
                <label class="input-group-text" for="pointsSelect"><i class="bi bi-filter me-2"></i>Select Band:</label>
                <select class="form-select" id="pointsSelect">
                {% for p in point_plots %}
                    <option value="{{ p.label }}"
                            data-src="{% url 'view_report' session_id p.file %}?chromeless=1"
                            data-full-src="{% url 'view_report' session_id p.file %}?source=qso"
                            {% if p.active %}selected{% endif %}>{{ p.label }}</option>
                {% endfor %}
                </select>
            </div>
            <div class="row">
                <div class="col-12 mb-4">
                    <div class="card shadow-sm">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span>Cumulative Points</span>
                            <a id="link-points" href="#" target="_blank" class="btn btn-xs btn-link text-muted"><i class="bi bi-box-arrow-up-right"></i></a>
                        </div>
                        <div class="card-body p-0">
                            <iframe id="frame-points" src="" class="viewport-frame"></iframe>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    document.addEventListener('DOMContentLoaded', function() {
        // --- Strategy Tab Logic ---
        const strategySelect = document.getElementById('strategySelect');
        const frameBreakdown = document.getElementById('frame-breakdown');
        const frameDiff = document.getElementById('frame-diff');
        const linkBreakdown = document.getElementById('link-breakdown');
        const linkDiff = document.getElementById('link-diff');
        const diffBandBtns = document.querySelectorAll('.diff-band-btn');
        let currentDiffBand = 'all';

        function updateStrategy() {
            if(!strategySelect) return;
            const selectedOption = strategySelect.options[strategySelect.selectedIndex];
            
            frameBreakdown.src = selectedOption.dataset.breakdown;
            linkBreakdown.href = selectedOption.dataset.fullBreakdown;
            
            updateDiffContent();
        }
        
        function updateDiffContent() {
            if (!strategySelect) return;
            const selectedOption = strategySelect.options[strategySelect.selectedIndex];
            
            let diffSrc = selectedOption.getAttribute('data-diff-' + currentDiffBand);
            if (!diffSrc) diffSrc = selectedOption.getAttribute('data-diff-all');
            if (diffSrc) {
                frameDiff.src = diffSrc;
                linkDiff.href = diffSrc.replace('?chromeless=1', '?source=qso');
            }
        }

        if(strategySelect) {
            updateStrategy();
            // Init
            strategySelect.addEventListener('change', updateStrategy);
        }
        
        diffBandBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                diffBandBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentDiffBand = btn.dataset.band;
                updateDiffContent();
            });
        });
        // --- Generic Dropdown Logic for other tabs ---
        function setupDropdown(selectId, frameId, linkId) {
            const select = document.getElementById(selectId);
            const frame = document.getElementById(frameId);
            const link = document.getElementById(linkId);
            
            if (!select || !frame) return;
            function update() {
                const opt = select.options[select.selectedIndex];
                frame.src = opt.dataset.src;
                if(link) link.href = opt.dataset.fullSrc;
            }
            
            update();
            // Init
            select.addEventListener('change', update);
        }

        setupDropdown('cumulSelect', 'frame-qso-rates', 'link-qso-rates');
        setupDropdown('ratesSelect', 'frame-rates', 'link-rates');
        setupDropdown('pointsSelect', 'frame-points', 'link-points');
    });
</script>
{% endblock %}
__CODE_BLOCK__

## 4. Pre-Flight Check
* **Verification:** `qso_dashboard.html` has CSS `.viewport-frame { height: 900px; ... }` and NO javascript auto-resizing logic.
* **Verification:** Confirmed valid Django syntax (all blocks closed).
* **Impact:** This definitively resolves the "thrashing" by enforcing a stable container for the (already fixed) Plotly charts.