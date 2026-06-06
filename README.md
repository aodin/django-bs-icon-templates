django-bs-icon-templates
========================

Django templates for [Bootstrap Icons](https://github.com/twbs/icons). Each SVG is pre-processed so the `width` attribute is removed and `height` becomes a Django template variable (`{{ height|default:16 }}`), letting you control icon size at render time.

### Installation

```bash
pip install django-bs-icon-templates
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "bs_icon_templates",
]
```

### Usage

Use `{% include %}` directly in a template:

```django
{% include "bs_icon/alarm.svg" with height=24 %}
```

Or as a template tag:

```django
{% load bs_icons %}

{% bs_icon "alarm" %}
{% bs_icon "alarm" height=24 %}
```


### Updating icons

If a newer Bootstrap Icons release is available, re-run the management command:

```bash
python manage.py download_bs_icons
```

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--version` | latest | Bootstrap Icons release tag, e.g. `v1.13.1` |
| `--output-dir` | package templates dir | Write icons elsewhere (e.g. your own app's templates) |


Happy hacking,

aodin
