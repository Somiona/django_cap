from django.db import models
from django.utils import timezone


class Challenge(models.Model):
    """
    Model to store active challenges
    """

    token = models.CharField(max_length=50, unique=True, db_index=True)
    challenge_data = models.JSONField(
        help_text=(
            "Challenge configuration object with {c: count, s: size, d: difficulty}"
        )
    )
    expires = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "django_cap_challenges"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Challenge {self.token[:8]}... (expires: {self.expires})"

    def is_expired(self):
        return timezone.now() > self.expires


class Token(models.Model):
    """
    Model to store validated tokens
    """

    token_hash = models.CharField(max_length=128, unique=True, db_index=True)
    token_id = models.CharField(max_length=16, db_index=True)
    expires = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "django_cap_tokens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Token {self.token_id} (expires: {self.expires})"

    def is_expired(self):
        return timezone.now() > self.expires
