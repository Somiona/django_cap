from django.contrib import admin

from django_cap.django_app_settings import (
    DJANGO_ADMIN_ENABLED,  # type: ignore
    UNFOLD_ADMIN_ENABLED,  # type: ignore
)
from django_cap.models import Challenge, Token

if DJANGO_ADMIN_ENABLED:
    if UNFOLD_ADMIN_ENABLED:
        from unfold.admin import ModelAdmin  # type: ignore
    else:
        from django.contrib.admin import ModelAdmin

    @admin.register(Challenge)
    class ChallengeAdmin(ModelAdmin):  # type: ignore
        list_display = ["token", "expires", "is_expired", "created_at"]
        list_filter = ["expires", "created_at"]
        search_fields = ["token"]
        readonly_fields = ["created_at"]
        ordering = ["-created_at"]

        def is_expired(self, obj):
            return obj.is_expired()

        is_expired.boolean = True  # type: ignore
        is_expired.short_description = "Expired"  # type: ignore

    @admin.register(Token)
    class TokenAdmin(ModelAdmin):  # type: ignore
        list_display = ["token_id", "expires", "is_expired", "created_at"]
        list_filter = ["expires", "created_at"]
        search_fields = ["token_id", "token_hash"]
        readonly_fields = ["created_at"]
        ordering = ["-created_at"]

        def is_expired(self, obj):
            return obj.is_expired()

        is_expired.boolean = True  # type: ignore
        is_expired.short_description = "Expired"  # type: ignore
