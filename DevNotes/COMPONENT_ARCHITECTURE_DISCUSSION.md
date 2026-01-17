# Recursive Component Architecture for Dashboards

## Problem Statement

The dashboard system needs to support:
- **Dashboards that are completely different OR the same** between contests
- **Panels within dashboards** that differ between contests
- **Panel structures** (tabs, selectors, content) that vary
- **Recursive composition** (dashboards → panels → sub-panels → widgets)
- **Third-level dashboards** (main → sub-dashboard → sub-sub-dashboard)
- **Pluggable components** without code changes per contest

---

## Current Structure Analysis

### Hierarchy (Levels 1-2):

```
Level 1: Main Dashboard (dashboard.html)
  └─ Panel: Scoreboard Table
  └─ Panel: Strategic Breakdown
      └─ Widget: Hourly Breakdown (link)
      └─ Widget: QSO Reports (link to Level 2)
      └─ Widget: Multiplier Reports (link to Level 2)

Level 2: Sub-Dashboards
  ├─ QSO Dashboard (qso_dashboard.html)
  │   ├─ Panel: Global Context (iframe)
  │   └─ Panel: Tabbed Interface
  │       ├─ Tab: Pairwise Strategy
  │       │   ├─ Selector: Matchup Dropdown
  │       │   ├─ Widget: Strategy Breakdown Chart (Plotly/JSON)
  │       │   └─ Widget: Rate Differential Chart (Plotly/JSON, band selector)
  │       ├─ Tab: QSOs by Band
  │       │   ├─ Selector: Band Dropdown
  │       │   └─ Widget: Cumulative QSO Rates Chart (Plotly/JSON)
  │       ├─ Tab: Rate Detail
  │       │   ├─ Selector: Log Dropdown
  │       │   └─ Widget: Rate Sheet (iframe)
  │       ├─ Tab: Points & Bands
  │       │   ├─ Selector: Band Dropdown
  │       │   └─ Widget: Points Chart (Plotly/JSON)
  │       └─ Tab: Band Activity Comparison
  │           ├─ Selector: Matchup Dropdown
  │           └─ Widget: Butterfly Chart (Plotly/JSON)
  │
  └─ Multiplier Dashboard (multiplier_dashboard.html)
      ├─ Panel: Scoreboard Cards
      ├─ Panel: Multiplier Breakdown (loop over totals)
      │   └─ Widget: Horizontal Bar Chart (HTML/CSS)
      └─ Panel: Band Spectrum
          └─ Tabs: All / Countries / Zones
              └─ Widget: Vertical Spectrum Chart (HTML/CSS)
```

### Key Patterns Identified:

1. **Panels** contain **widgets** and/or **selectors**
2. **Tabs** are panels with multiple content areas
3. **Selectors** control widget data
4. **Widgets** render data (charts, iframes, tables, HTML)
5. **Navigation** links to other dashboards

---

## Proposed Architecture: Component-Based System

### Core Concept: Recursive Component Tree

```
Dashboard (Level 1/2/3)
  └─ Panel[]
      └─ Widget[] OR SubPanel[]
          └─ Widget[] OR SubPanel[]
              └─ ...
```

**Configuration-Driven**: Each component defined in JSON config, rendered recursively.

---

## Component Types

### 1. Dashboard Component
- **Purpose**: Top-level container, defines layout, navigation
- **Properties**: 
  - `id`, `title`, `layout` (single-column, multi-column, tabbed)
  - `panels`: Array of panel components
  - `navigation`: Links to other dashboards

### 2. Panel Component
- **Purpose**: Container for widgets and/or sub-panels
- **Properties**:
  - `id`, `title`, `layout`
  - `type`: `simple`, `tabs`, `accordion`, `grid`
  - `selectors`: Array of selector components (optional)
  - `widgets`: Array of widget components (optional)
  - `panels`: Array of sub-panel components (recursive, optional)

### 3. Selector Component
- **Purpose**: Control widget data (dropdowns, buttons, filters)
- **Properties**:
  - `id`, `label`, `type`: `dropdown`, `radio`, `checkbox`, `button_group`
  - `options`: Array of `{value, label, data_attributes}`
  - `target`: Widget ID(s) this selector controls
  - `default_value`: Initial selection

### 4. Widget Component
- **Purpose**: Render data (chart, iframe, table, HTML)
- **Properties**:
  - `id`, `title`, `type`: `chart_plotly`, `iframe`, `table`, `html`, `link_card`
  - `data_source`: How to get data (artifact_id, context_key, computed)
  - `config`: Widget-specific configuration
  - `dependencies`: Selector IDs that affect this widget

---

## Configuration Structure

### Contest Definition Extension:

```json
{
  "contest_name": "CQ-WW-CW",
  "dashboard": {
    "template": "component_dashboard.html",  // Generic renderer
    "layout": {
      "type": "single_column",
      "panels": [
        {
          "id": "scoreboard",
          "type": "simple",
          "widgets": [
            {
              "id": "scoreboard_table",
              "type": "table",
              "title": "The Scoreboard",
              "data_source": {
                "type": "context",
                "key": "logs"
              },
              "config": {
                "columns": ["callsign", "qsos", "run_qsos", "run_percent", "mults", "score"],
                "mult_headers_source": "context.mult_headers"
              }
            }
          ]
        },
        {
          "id": "strategic_breakdown",
          "type": "simple",
          "title": "Strategic Breakdown",
          "widgets": [
            {
              "id": "hourly_breakdown",
              "type": "link_card",
              "title": "Hourly Breakdown",
              "icon": "bi-film",
              "data_source": {
                "type": "artifact",
                "report_id": "interactive_animation",
                "suffix": "--{combo_id}.html"
              }
            },
            {
              "id": "qso_dashboard_link",
              "type": "link_card",
              "title": "QSO Reports",
              "icon": "bi-bar-chart-line",
              "target_dashboard": "qso"
            },
            {
              "id": "multiplier_dashboard_link",
              "type": "link_card",
              "title": "Multiplier Reports",
              "icon": "bi-table",
              "target_dashboard": "multiplier"
            }
          ]
        }
      ]
    }
  },
  "sub_dashboards": {
    "qso": {
      "layout": {
        "type": "single_column",
        "panels": [
          {
            "id": "global_context",
            "type": "simple",
            "widgets": [
              {
                "id": "global_qso_rate",
                "type": "iframe",
                "data_source": {
                  "type": "artifact",
                  "report_id": "qso_rate_plots_all",
                  "suffix": "--{combo_id}.html"
                }
              }
            ]
          },
          {
            "id": "qso_tabs",
            "type": "tabs",
            "panels": [
              {
                "id": "pairwise_strategy",
                "title": "Pairwise Strategy",
                "icon": "bi-chess",
                "conditional": "!is_solo",
                "selectors": [
                  {
                    "id": "matchup_selector",
                    "type": "dropdown",
                    "label": "Select Matchup:",
                    "icon": "bi-people",
                    "options": {
                      "type": "context",
                      "key": "matchups",
                      "value_template": "{{forloop.counter}}",
                      "label_template": "{{m.label}}",
                      "data_attributes": {
                        "breakdown-json": "{{m.qso_breakdown_json}}",
                        "breakdown-full": "{% url 'view_report' session_id m.qso_breakdown_file %}"
                      }
                    },
                    "default_value": "1"
                  }
                ],
                "widgets": [
                  {
                    "id": "strategy_breakdown_chart",
                    "type": "chart_plotly",
                    "title": "Strategy Breakdown (Uniques)",
                    "dependencies": ["matchup_selector"],
                    "data_source": {
                      "type": "dynamic_json",
                      "attribute": "data-breakdown-json"
                    }
                  },
                  {
                    "id": "rate_differential_chart",
                    "type": "chart_plotly",
                    "title": "Rate Differential",
                    "dependencies": ["matchup_selector", "band_selector"],
                    "data_source": {
                      "type": "dynamic_json",
                      "attribute": "data-diff-json-{band}"
                    },
                    "config": {
                      "selector": {
                        "id": "band_selector",
                        "type": "button_group",
                        "options": {
                          "type": "context",
                          "key": "valid_bands"
                        }
                      }
                    }
                  }
                ]
              },
              {
                "id": "qso_by_band",
                "title": "QSOs by Band",
                "icon": "bi-graph-up-arrow",
                "selectors": [
                  {
                    "id": "band_selector_qso",
                    "type": "dropdown",
                    "label": "Select Band:",
                    "options": {
                      "type": "context",
                      "key": "qso_band_plots"
                    }
                  }
                ],
                "widgets": [
                  {
                    "id": "cumulative_qso_chart",
                    "type": "chart_plotly",
                    "dependencies": ["band_selector_qso"],
                    "data_source": {
                      "type": "dynamic_json",
                      "attribute": "data-json-src"
                    }
                  }
                ]
              }
              // ... more tabs
            ]
          }
        ]
      }
    },
    "multiplier": {
      "layout": {
        "type": "single_column",
        "panels": [
          // ... multiplier-specific panels
        ]
      }
    }
  }
}
```

---

## Rendering System

### Template Structure:

```
templates/analyzer/
  components/
    dashboard.html              # Generic dashboard renderer
    panel_simple.html           # Simple panel renderer
    panel_tabs.html             # Tabbed panel renderer
    widget_table.html           # Table widget renderer
    widget_chart_plotly.html    # Plotly chart widget renderer
    widget_iframe.html          # Iframe widget renderer
    widget_link_card.html       # Link card widget renderer
    selector_dropdown.html      # Dropdown selector renderer
    selector_button_group.html  # Button group selector renderer
```

### Generic Dashboard Template (`components/dashboard.html`):

```django
{% extends 'base.html' %}
{% load component_tags %}

{% block content %}
  {% dashboard_header dashboard.config %}
  
  {% for panel_config in dashboard.config.layout.panels %}
    {% render_panel panel_config dashboard.context %}
  {% endfor %}
  
  {% dashboard_footer dashboard.config %}
{% endblock %}
```

### Recursive Panel Renderer (Template Tag):

```python
# templatetags/component_tags.py

@register.inclusion_tag('analyzer/components/panel_simple.html', takes_context=True)
def render_panel(context, panel_config):
    """Recursively render panel and its children."""
    panel_context = {
        'panel': panel_config,
        'parent_context': context,
    }
    
    # Resolve widgets
    if 'widgets' in panel_config:
        panel_context['widgets'] = [
            resolve_widget(w, context) for w in panel_config['widgets']
        ]
    
    # Resolve sub-panels (recursive)
    if 'panels' in panel_config:
        panel_context['panels'] = [
            {'config': p, 'context': context} 
            for p in panel_config['panels']
        ]
    
    return panel_context

def resolve_widget(widget_config, context):
    """Resolve widget data source."""
    data_source = widget_config.get('data_source', {})
    source_type = data_source.get('type')
    
    if source_type == 'context':
        # Get from context dictionary
        key = data_source['key']
        return context.get(key)
    elif source_type == 'artifact':
        # Discover artifact from manifest
        report_id = data_source['report_id']
        suffix = data_source['suffix']
        return discover_artifact(context['session_id'], report_id, suffix)
    elif source_type == 'dynamic_json':
        # Resolved by JavaScript from selector data attributes
        return None  # Frontend handles this
    # ... more source types
    
    return None
```

---

## View Layer Changes

### Generic Dashboard View:

```python
def dashboard_view(request, session_id, dashboard_type='main'):
    """Generic dashboard renderer driven by configuration."""
    session_path = os.path.join(settings.MEDIA_ROOT, 'sessions', session_id)
    context_path = os.path.join(session_path, 'dashboard_context.json')
    
    # Load base context
    with open(context_path, 'r') as f:
        base_context = json.load(f)
    
    # Load contest definition
    contest_name = base_context['contest_name']
    contest_def = ContestDefinition.from_json(contest_name)
    
    # Get dashboard configuration
    if dashboard_type == 'main':
        dashboard_config = contest_def.dashboard_config
    else:
        dashboard_config = contest_def.sub_dashboards.get(dashboard_type)
    
    if not dashboard_config:
        raise Http404(f"Dashboard '{dashboard_type}' not configured for {contest_name}")
    
    # Enhance context with dashboard-specific data
    enhanced_context = enhance_context_for_dashboard(
        base_context, 
        dashboard_config, 
        session_path
    )
    
    # Render generic template
    return render(request, 'analyzer/components/dashboard.html', {
        'dashboard': {
            'config': dashboard_config,
            'context': enhanced_context
        }
    })
```

### Context Enhancement:

```python
def enhance_context_for_dashboard(base_context, dashboard_config, session_path):
    """Add dashboard-specific data to context."""
    enhanced = base_context.copy()
    
    # Discover artifacts if needed
    if needs_artifact_discovery(dashboard_config):
        manifest_dir = discover_manifest_dir(session_path)
        artifacts = ManifestManager(manifest_dir).load()
        enhanced['artifacts'] = artifacts
        enhanced['manifest_dir'] = manifest_dir
    
    # Add computed values
    enhanced['is_solo'] = len(base_context.get('logs', [])) == 1
    enhanced['valid_bands'] = get_valid_bands_for_contest(base_context['contest_name'])
    
    return enhanced
```

---

## URL Routing Changes

```python
# urls.py
urlpatterns = [
    # Generic dashboard routing
    path('report/<str:session_id>/dashboard/', 
         views.dashboard_view, 
         {'dashboard_type': 'main'}, 
         name='dashboard_view'),
    path('report/<str:session_id>/dashboard/<str:dashboard_type>/', 
         views.dashboard_view, 
         name='sub_dashboard_view'),
]
```

**Benefits:**
- Single view handles all dashboards
- Dashboard type determined by URL, not hardcoded
- Supports unlimited dashboard levels

---

## Data Flow Pattern

### Static Data (Context-Based):
```
Contest Definition → Dashboard Config → View → Context → Template
```

### Dynamic Data (Selector-Driven):
```
Selector Change → JavaScript Event → Update Widget Data Attribute → 
Load New JSON → Re-render Widget
```

### Artifact-Based Data:
```
Report Generator → Manifest → View Discovers Artifact → 
Context → Template → Widget Renders
```

---

## Implementation Phases

### Phase 1: Foundation (Now)
1. Create component template structure
2. Implement basic template tags (`render_panel`, `render_widget`)
3. Create widget renderers (table, iframe, link_card)
4. Test with simple dashboard (scoreboard + links)

### Phase 2: Selectors & Dynamic Widgets (After Phase 1)
1. Implement selector components (dropdown, button_group)
2. Implement JavaScript data binding system
3. Implement dynamic JSON loading for charts
4. Test with QSO dashboard tabs

### Phase 3: Recursive Panels (After Phase 2)
1. Implement nested panel support
2. Test with complex tabbed interfaces
3. Test with third-level dashboards

### Phase 4: Configuration System (After Phase 3)
1. Extend `ContestDefinition` to load dashboard configs
2. Migrate CQ-WW to configuration
3. Build ARRL 10 using configuration

### Phase 5: Advanced Features (Future)
1. Panel conditional rendering (`conditional: "!is_solo"`)
2. Computed data sources
3. Widget dependency chains
4. Panel caching/performance optimization

---

## Benefits of This Architecture

### 1. **Scalability**
- Add new contests: Just add JSON config, no code changes
- Add new dashboards: Define in `sub_dashboards` config
- Add new widgets: Create widget renderer, register in config

### 2. **Flexibility**
- Contests can have completely different dashboards
- Contests can share dashboard structures
- Panels can be rearranged per contest
- Widgets can be mixed and matched

### 3. **Maintainability**
- Single renderer for all dashboards
- Reusable widget components
- Clear separation: Config (what) vs Renderers (how)
- Changes to widget rendering affect all dashboards

### 4. **Testability**
- Configuration can be validated independently
- Widget renderers can be unit tested
- Context enhancement can be tested separately

### 5. **Recursive Composition**
- Panels can contain panels (tabs, accordions, nested grids)
- Supports unlimited nesting depth
- Each level follows same pattern

---

## Challenges & Considerations

### 1. **Complexity**
- **Risk**: System becomes too abstract
- **Mitigation**: Start simple, add complexity only as needed
- **Guideline**: Prefer explicit config over magic

### 2. **Performance**
- **Risk**: Recursive rendering may be slow
- **Mitigation**: Cache resolved artifacts, lazy-load heavy widgets
- **Guideline**: Profile before optimizing

### 3. **JavaScript Integration**
- **Risk**: Dynamic widgets require JS coordination
- **Mitigation**: Standardize data binding pattern, document clearly
- **Guideline**: Keep JS simple, data-driven

### 4. **Migration Path**
- **Risk**: Migrating existing dashboards is labor-intensive
- **Mitigation**: Migrate incrementally, keep old templates working
- **Guideline**: One dashboard at a time, test thoroughly

### 5. **Configuration Validation**
- **Risk**: Invalid configs cause runtime errors
- **Mitigation**: Validate configs on load, provide clear error messages
- **Guideline**: Fail fast, fail clearly

---

## Decision: Should We Do This?

### Arguments FOR:
- ✅ **Future-Proof**: Supports unlimited contest variation
- ✅ **Scalable**: Add contests without code changes
- ✅ **Flexible**: Recursive composition handles complex layouts
- ✅ **Maintainable**: Single renderer vs many templates

### Arguments AGAINST:
- ❌ **Complex**: Significant upfront work
- ❌ **Over-Engineering**: May be more than needed for 2-3 contests
- ❌ **Learning Curve**: Team needs to understand component system
- ❌ **Migration Cost**: Refactoring existing dashboards is work

### Recommendation: **Hybrid Approach**

1. **Phase 1**: Extract common partials (simple, immediate value)
2. **ARRL 10**: Build using partials, learn requirements
3. **Evaluate**: After ARRL 10, decide if full component system needed

**If after ARRL 10 we have:**
- 2-3 similar dashboards → Partial system sufficient
- Very different dashboards → Full component system needed
- Need third-level → Component system likely needed

**Decision Point**: After ARRL 10 implementation, reassess.

---

## Alternative: Simplified Component System

If full system is too complex, consider **"Panel Registry"** approach:

```python
# Simpler: Just register panels, compose manually

PANEL_REGISTRY = {
    'scoreboard_table': ScoreboardTablePanel,
    'strategic_breakdown_links': StrategicBreakdownPanel,
    'qso_tabs': QSOTabsPanel,
}

# In contest config:
{
  "dashboard": {
    "panels": ["scoreboard_table", "strategic_breakdown_links"]
  }
}

# View:
panels = [PANEL_REGISTRY[p]() for p in config['panels']]
```

**Trade-off**: Less flexible but much simpler to implement and understand.

---

## Final Recommendation

**Start simple, scale up as needed:**

1. ✅ **Do Phase 1 now** (extract partials)
2. ✅ **Build ARRL 10** (learn requirements)
3. ✅ **After ARRL 10** (evaluate need for component system)

If ARRL 10 reveals:
- Simple differences → Partial system sufficient
- Complex differences → Full component system
- Third-level needed → Component system required

**Don't build component system until you know you need it, but design for it to be possible.**
