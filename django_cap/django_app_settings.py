from django.apps import apps

DJANGO_APP_SETTINGS_PREFIX = "CAP_"

__all__ = [
    "SITES_ENABLED",  # noqa: F822 # type: ignore
    "ENABLED",  # noqa: F822 # type: ignore
    "NINJA_API_ENABLED",  # noqa: F822 # type: ignore
    "NINJA_API_ENABLE_DOCS",  # noqa: F822 # type: ignore
    "DRF_API_ENABLED",  # noqa: F822 # type: ignore
    "UNFOLD_ADMIN_ENABLED",  # noqa: F822 # type: ignore
    "WIDGET_URL",  # noqa: F822 # type: ignore
    "CHALLENGE_COUNT",  # noqa: F822 # type: ignore
    "CHALLENGE_SIZE",  # noqa: F822 # type: ignore
    "CHALLENGE_DIFFICULTY",  # noqa: F822 # type: ignore
    "CHALLENGE_EXPIRES_S",  # noqa: F822 # type: ignore
    "TOKEN_EXPIRES_S",  # noqa: F822 # type: ignore
    "CLEANUP_INTERVAL_S",  # noqa: F822 # type: ignore
]


class DjangoAppSettings:
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from django.conf import settings

        return getattr(settings, self.prefix + name, dflt)

    @property
    def SITES_ENABLED(self):
        return apps.is_installed("django.contrib.sites")

    @property
    def DJANGO_ADMIN_ENABLED(self):
        return apps.is_installed("django.contrib.admin")

    @property
    def ENABLED(self):
        return apps.is_installed("django_cap")

    @property
    def NINJA_API_ENABLED(self):
        return apps.is_installed("django_cap.ninja_api")

    @property
    def NINJA_API_ENABLE_DOCS(self):
        return self._setting("NINJA_API_ENABLE_DOCS", True)

    @property
    def DRF_API_ENABLED(self):
        return apps.is_installed("django_cap.drf_api")

    @property
    def UNFOLD_ADMIN_ENABLED(self):
        return apps.is_installed("unfold")

    # @property
    # def HEADLESS_ONLY(self):
    #     return self._setting("HEADLESS_ONLY", False)

    @property
    def WIDGET_URL(self):
        return self._setting(
            "WIDGET_URL", "https://cdn.jsdelivr.net/npm/@cap.js/widget@0.1.25"
        )

    @property
    def CHALLENGE_COUNT(self):
        return self._setting("CHALLENGE_COUNT", 50)

    @property
    def CHALLENGE_SIZE(self):
        return self._setting("CHALLENGE_SIZE", 32)

    @property
    def CHALLENGE_DIFFICULTY(self):
        return self._setting("CHALLENGE_DIFFICULTY", 4)

    @property
    def CHALLENGE_EXPIRES_S(self):
        return self._setting("CHALLENGE_EXPIRES_S", 30)

    @property
    def TOKEN_EXPIRES_S(self):
        return self._setting("TOKEN_EXPIRES_S", 10 * 60)

    @property
    def CLEANUP_INTERVAL_S(self):
        return self._setting("CLEANUP_INTERVAL_S", 60)


_django_app_settings = DjangoAppSettings(DJANGO_APP_SETTINGS_PREFIX)


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_django_app_settings, name)
