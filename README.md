[![django_cap_tests](https://github.com/somiona/django_cap/actions/workflows/test.yml/badge.svg)](https://github.com/somiona/django_cap/actions/workflows/test.yml)
[![cov](https://somiona.github.io/django_cap/badges/coverage.svg)](https://github.com/somiona/django_cap/actions)
[![release](https://img.shields.io/github/v/release/somiona/django_cap)](https://github.com/Somiona/django_cap/releases)
[![downloads](https://img.shields.io/pypi/dm/https://pypi.org/project/django_cap/)](https://pypi.org/project/django_cap/)
## Django Cap
This is a implementation of [Cap.js](https://capjs.js.org/) Server for Django, which provides challenge generation and verification for PoW (Proof of Work) captcha. See

## Usage
### Installation
To install the package, simply run:
```bash
pip install django_cap
```

If you want to use the Django Ninja integration, you can install it with:
```bash
pip install django_cap[ninja]
```

Or if you want to use the Django Rest Framework integration, you can install it with:
```bash
pip install django_cap[drf]
```

Note that currently, only ninja integration and vanilla Django Json views are implemented, DRF integration will be added shortly.

### Configuration
To use this package, you need to add `django_cap` to your `INSTALLED_APPS` in your Django settings file:
```python
INSTALLED_APPS = [
    ...
    'django_cap',
    'django_cap.ninja',  # Add this if you want enable ninja integration
]
```

You need to configure the url patterns in your Django project's `urls.py` file:
```python

urlpatterns = [
    ...
    path("cap/", include("django_cap.urls")),
    ...
]
```

You can access the api at `/cap/v1/[challenge|redeem|validate]` endpoints. This is compatible with Cap.js/widgets. If your frontend is not hosted by Django, you need to refer Cap.js documentation for the installation, and simply configure the api endpoint as following:
```html
<cap-widget id="cap" data-cap-api-endpoint="https://your-api-site/cap/v1/"></cap-widget>
```

By default, ninja doc will be avaliable at `/cap/v1/docs/` and `/cap/v1/openapi.json`. If you want to disable the ninja doc, you can disable it in your Django settings file:

```python
#django_settings.py
...
CAP_NINJA_API_ENABLE_DOCS = False
...
```

### Use with Django Templates
This package also provides a custom template tag to render the captcha widget in your Django templates. You can use it as follows:
```django html
{% load django_cap %}
<head>
    ...
    <!-- Load the CAP widget script using template tag -->
    {% cap_widget_script %}
    ...
</head>
<body>
    ...
    <!-- Render the CAP widget -->
    {% cap_widget %}
    ...
</body>
```
**TODO**: token validation procedure for Django templates is not implemented yet, currently we only provide the widget rendering. Help welcome if you are familiar with Django templates.

### Configuration Options
- `CAP_NINJA_API_ENABLE_DOCS`: Enable or disable the ninja API docs. Default is `True`.
- `CAP_CHALLENGE_COUNT`: The number of answer required for one challenge. Default is 50.
- `CAP_CHALLENGE_SIZE`: The size of the challenge string. Default is 32.
- `CAP_CHALLENGE_DIFFICULTY`: The difficulty of the challenge, Default is 4
- `CAP_CHALLENGE_EXPIRES_S`: The expiration time of the challenge in seconds. Default is 30 seconds.
- `CAP_TOKEN_EXPIRES_S`: The expiration time of the token in seconds. Default is 10 minutes.
- `CAP_CLEANUP_INTERVAL_S`: The interval for cleaning up expired challenges and tokens in seconds. Default is 60 seconds.


## Dev environment setup
1. Clone this repository.
2. Make sure you have python 3.13 installed.
    ```bash
    python --version
    ```
3. Make sure you have uv installed.
    ```bash
    # for MacOS, recommend using homebrew
    brew install uv
    ```
    ```bash
    # for Linux, recommend using their installer
    # curl
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # wget
    wget -qO- https://astral.sh/uv/install.sh | sh
    ```
    ```powershell
    # for Windows, recommend using WinGet
    winget install --id=astral-sh.uv  -e
    # you can also use scoop
    scoop install main/uv
    ```
4. Install the dependencies:
    ```bash
    uv sync
    ```

5. Activate the virtual environment:
    ```bash
    # for linux/macOS
    source .venv/bin/activate
    ```
    ```powershell
    # for windows
    .\.venv\Scripts\Activate.ps1
    ```

6. Run tests:
    ```bash
    uv run pytest
    ```

7. Run linting and formatting:
    ```bash
    # Check code quality
    uv run ruff check

    # Format code
    uv run ruff format
    ```

8. Build the package:
    ```bash
    uv run pdm build
    ```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Links
- [GitHub Repository](https://github.com/somiona/django-cap)
- [PyPI Package](https://pypi.org/project/django-cap/)
- [Cap.js Project](https://capjs.js.org/)
