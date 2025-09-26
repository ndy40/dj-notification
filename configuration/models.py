import re
import secrets
import string
import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

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


class Template(models.Model):
    """Represents a notification template with auto-computed variables list."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    service = models.ForeignKey("Service", on_delete=models.CASCADE, related_name="templates", null=True, blank=True)
    template = models.TextField(help_text="Message body with placeholders like {{ variable }}")
    # Computed application-side from `template` before save
    variables = models.JSONField(default=list, blank=True, editable=False)
    version = models.IntegerField(default=1)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "templates"
        ordering = ["-created_at"]
        verbose_name = "Template"
        verbose_name_plural = "Templates"

    VARIABLE_PATTERN = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_\.\-]*)\s*}}")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.title} v{self.version}"

    def save(self, *args, **kwargs):
        # Compute variables from the template body on every save
        self.variables = self._extract_variables(self.template)
        super().save(*args, **kwargs)

    @staticmethod
    def _extract_variables(text: str) -> list[str]:
        if not text:
            return []
        # Preserve first-seen order and ensure uniqueness
        seen = set()
        vars_ordered: list[str] = []
        for match in Template.VARIABLE_PATTERN.finditer(text):
            var = match.group(1)
            if var not in seen:
                seen.add(var)
                vars_ordered.append(var)
        return vars_ordered


class Service(models.Model):
    """Represents an application/service that uses a Provider with SDK config and templates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255, blank=True)
    api_expires_on = models.DateTimeField(null=True, blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="services")
    config = models.JSONField(default=dict, blank=True, help_text="Key-value SDK parameters")
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services"
        ordering = ["name"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name

    def save(self, *args, **kwargs):
        # Run model validation so admin shows errors instead of crashing.
        self.full_clean()

        # Auto-generate api_key if not provided
        if not getattr(self, "api_key", None):
            self.api_key = self._generate_api_key()
        # Default api_expires_on to one year from now if not set
        if not self.api_expires_on:
            self.api_expires_on = timezone.now() + timedelta(days=365)
        super().save(*args, **kwargs)

    def clean(self):
        """Validate the service before saving.

        Ensures that the config matches the provider's expected schema. Errors are
        attached to the 'config' field so Django Admin can display them inline.
        """
        errors = {}
        schema_cls = None
        if getattr(self, "provider", None):
            schema_cls = self.provider.get_schema_class()
        if schema_cls:
            try:
                schema_cls(**(self.config or {}))
            except TypeError:
                errors.setdefault("config", []).append(f"Invalid configuration for provider '{self.provider.code}'")
            except Exception:
                errors.setdefault("config", []).append(f"Invalid configuration for provider '{self.provider.code}'")
        if errors:
            raise ValidationError(errors)

    def _generate_api_key(self, total_length: int = 32, prefix: str = "svc_") -> str:
        """Instance wrapper around module-level _generate_api_key."""
        return _generate_api_key(total_length=total_length, prefix=prefix)


def _generate_api_key(total_length: int = 32, prefix: str = "svc_") -> str:
    """Generate a secure API key of exact total_length with the given prefix.
    Uses URL-safe characters [a-zA-Z0-9] to avoid punctuation.
    """
    if total_length <= len(prefix):
        # Fallback to just prefix if misconfigured
        return prefix
    alphabet = string.ascii_letters + string.digits
    remaining = total_length - len(prefix)
    suffix = "".join(secrets.choice(alphabet) for _ in range(remaining))
    return f"{prefix}{suffix}"
