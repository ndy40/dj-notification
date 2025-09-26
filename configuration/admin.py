from django.contrib import admin
from django.utils.safestring import mark_safe

from common.markdown import render_markdown_safe

from .mixins import AdminReadOnlyMixin
from .models import Provider


@admin.register(Provider)
class ProviderAdmin(AdminReadOnlyMixin, admin.ModelAdmin):
    list_display = ("name", "code", "type")
    search_fields = ("name", "code")  # 1) Search by name or code
    list_filter = ("type",)  # 2) Filter by type

    # Control the order of fields on the admin detail page
    fields = ("name", "code", "type", "schema_documentation", "request_schema_documentation")

    # Extra read-only computed/documentation fields
    extra_readonly_fields = ("schema_documentation", "request_schema_documentation")

    def schema_doc_short(self, obj: Provider) -> str:
        doc = obj.schema_doc() if hasattr(obj, "schema_doc") else ""
        return (doc.splitlines()[0] if doc else "-")[:200]

    schema_doc_short.short_description = "Schema Doc"

    def schema_documentation(self, obj: Provider) -> str:
        doc = obj.schema_doc() if hasattr(obj, "schema_doc") else ""
        if not doc:
            return "No documentation available for this provider schema."

        html = render_markdown_safe(doc)
        return mark_safe(html)

    schema_documentation.short_description = "Schema Documentation"

    def request_schema_documentation(self, obj: Provider) -> str:
        doc = obj.request_schema_doc() if hasattr(obj, "request_schema_doc") else ""
        if not doc:
            return "No documentation available for this provider request schema."

        html = render_markdown_safe(doc)
        return mark_safe(html)

    request_schema_documentation.short_description = "Request Schema Documentation"
