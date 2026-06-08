django-bs-icon-templates
========================

Django templates for [Bootstrap Icons](https://github.com/twbs/icons), which allows you to `include` them directly into other templates. Each SVG is pre-processed to make `height` a template variable that defaults to 16.

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

### As a development dependency

The preprocessed icons are about 8mb in file size. If you only need a few icons, you can install `django-bs-icon-templates` as a dev dependency and copy icons into the template directory of your choice:

```bash
python manage.py copy_bs_icons alarm gear github
```

Icon names may be given with or without the `.svg` suffix.

Once the `bs_icon_templates` is removed from `INSTALLED_APPS`, remember that only the `include` method above will work for your vendored icons.

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--output-dir` | `BASE_DIR/templates/bs_icon` | Destination directory |
| `--source-dir` | package templates dir | Source directory |


Happy hacking,

aodin
