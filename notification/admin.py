from django.contrib import admin
from django.utils.safestring import mark_safe

from common.markdown import render_markdown_safe

from .mixins import AdminReadOnlyMixin
from .models import Notification, Provider, Service, Template


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


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "service", "created_at", "updated_at")
    list_filter = ("enabled",)
    search_fields = ("title", "subject", "service__name")
    readonly_fields = ("variables", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "subject", "service", "version", "enabled")}),
        ("Content", {"fields": ("template",)}),
        ("Computed/Metadata", {"fields": ("variables", "created_at", "updated_at")}),
    )


class TemplateInline(admin.TabularInline):
    model = Template
    fields = ("title", "subject", "version", "enabled")
    readonly_fields = ("title", "subject", "version", "enabled")
    can_delete = False
    extra = 0
    max_num = 0
    show_change_link = True


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "provider", "enabled", "api_expires_on", "created_at")
    list_filter = ("enabled", "provider__type")
    search_fields = ("name", "provider__name", "provider__code")
    readonly_fields = ("created_at", "updated_at")
    inlines = [TemplateInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "enabled",
                )
            },
        ),
        ("Provider/Auth", {"fields": ("provider", "api_key", "api_expires_on")}),
        ("Configuration", {"fields": ("config",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "service",
        "type",
        "status",
        "http_status",
        "retry_count",
        "created_at",
        "update_at",
    )
    list_filter = ("status", "type", "service__provider__type")
    search_fields = ("id", "request_id", "service__name", "service__provider__name")
    readonly_fields = ("created_at", "update_at")
    fieldsets = (
        (None, {"fields": ("service", "template_ref", "request_id")}),
        ("Content", {"fields": ("content", "plain_text")}),
        ("Delivery", {"fields": ("type", "status", "retry_count", "http_status")}),
        ("Payload/Response", {"fields": ("payload_config", "provider_response")}),
        ("Timestamps", {"fields": ("created_at", "update_at")}),
    )
