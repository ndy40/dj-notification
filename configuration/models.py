import uuid

from django.db import models

from .mixins import ProviderConfigSchemaMixin, ProviderRequestMixin


class Provider(ProviderConfigSchemaMixin, ProviderRequestMixin, models.Model):
    """Represents an outbound notification provider configuration."""

    class ProviderType(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=100,
        unique=True,
        help_text=(
            "Provider code maps to a module under provider/{code}.py, e.g., "
            '"PROVIDER NAME" -> "provider_name.py" or "providername.py".'
        ),
    )
    type = models.CharField(max_length=20, choices=ProviderType.choices)

    class Meta:
        db_table = "providers"
        ordering = ["name"]
        verbose_name = "Provider"
        verbose_name_plural = "Providers"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.name} ({self.get_type_display()})"
