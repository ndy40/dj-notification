import inspect
import re


class NameCamelizeMixin:
    """Provides a helper to convert snake/kebab/spaced to CamelCase."""

    @staticmethod
    def _camelize(value: str) -> str:
        """Convert strings like 'mailgun', 'mail_gun', 'mail-gun' to 'Mailgun'."""
        parts = re.split(r"[_\-\s]+", value.strip()) if value else []
        return "".join(p.capitalize() for p in parts if p)


class ProviderConfigSchemaMixin(NameCamelizeMixin):
    """Helpers to resolve and document a provider configuration schema class.

    Expects the consumer to define `code` and `type` attributes (as Provider does).
    """

    def _schema_class_candidates(self) -> list[str]:
        base = f"{self._camelize(self.code)}{self._camelize(self.type)}"
        # Try with and without the 'Config' suffix to be lenient with naming.
        return [f"{base}Config", base]

    def get_schema_class(self):
        """Return the schema class for this provider or None if not found.

        The lookup is performed in configuration.schema.config module, trying both
        '<Code><Type>Config' and '<Code><Type>' class names. For example,
        'mailgun' + 'email' resolves to 'MailgunEmail' (matches current repo).
        """
        try:
            from .schema import config as schema_config
        except Exception:
            return None

        for name in self._schema_class_candidates():
            cls = getattr(schema_config, name, None)
            if isinstance(cls, type):
                return cls
        return None

    def schema_doc(self) -> str:
        """Return the cleaned docstring for the resolved schema class, if any.

        Returns an empty string if the class or its docstring is missing.
        """
        cls = self.get_schema_class()
        if not cls:
            return ""
        doc = getattr(cls, "__doc__", None)
        return inspect.cleandoc(doc) if doc else ""


class ProviderRequestMixin(NameCamelizeMixin):
    """Helpers to resolve and document a provider request schema class.

    The request schema class lives in configuration.schema.request and its name is
    derived as '<Code><Type>Request', e.g., 'MailgunEmailRequest'.
    Expects the consumer to define `code` and `type` attributes (as Provider does).
    """

    def _request_schema_class_candidates(self) -> list[str]:
        base = f"{self._camelize(self.code)}{self._camelize(self.type)}"
        return [f"{base}Request"]

    def get_request_schema_class(self):
        """Return the request schema class for this provider or None if not found."""
        try:
            from .schema import request as schema_request
        except Exception:
            return None

        for name in self._request_schema_class_candidates():
            cls = getattr(schema_request, name, None)
            if isinstance(cls, type):
                return cls
        return None

    def request_schema_doc(self) -> str:
        """Return the cleaned docstring for the resolved request schema class."""
        cls = self.get_request_schema_class()
        if not cls:
            return ""
        doc = getattr(cls, "__doc__", None)
        return inspect.cleandoc(doc) if doc else ""


class AdminReadOnlyMixin:
    """A mixin to make Django admin classes fully read-only.

    Usage:
      class MyModelAdmin(AdminReadOnlyMixin, admin.ModelAdmin):
          extra_readonly_fields = ("some_computed_field",)
    """

    # Disable bulk actions
    actions = None

    # Permissions: disallow add/change/delete; allow view
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def get_readonly_fields(self, request, obj=None):
        """Mark all model fields as read-only and merge in any extra ones.

        Child classes can declare `extra_readonly_fields` as an iterable of field
        names to include in addition to the model fields.
        """
        # Collect concrete model fields if model is available
        model_fields = []
        if getattr(self, "model", None) is not None and hasattr(self.model, "_meta"):
            model_fields = [f.name for f in self.model._meta.fields]
        extra = tuple(getattr(self, "extra_readonly_fields", ()))
        return tuple(sorted(set(list(model_fields) + list(extra))))
