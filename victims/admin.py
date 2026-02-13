from django.contrib import admin
from django.forms import model_to_dict

from .models import AuditLog, Photo, Source, Submission, Tag, Victim, VictimTag


def log_action(user, action, obj, changes=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        target_model=obj.__class__.__name__,
        target_id=getattr(obj, "pk", None),
        changes=changes or {},
    )


class NoDeleteForModerator:
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name="Moderator").exists():
            return False
        return super().has_delete_permission(request, obj)


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ("image", "caption", "photographer_credit", "order_index")


class SourceInline(admin.TabularInline):
    model = Source
    extra = 1
    fields = ("title", "url", "publisher_name", "publication_date", "credibility_score")


class VictimTagInline(admin.TabularInline):
    model = VictimTag
    extra = 1


@admin.register(Victim)
class VictimAdmin(NoDeleteForModerator, admin.ModelAdmin):
    list_display = (
        "full_name",
        "verification_status",
        "city_of_death",
        "country",
        "date_of_death",
        "confidence_score",
    )
    search_fields = ("full_name", "native_name", "biography")
    list_filter = ("verification_status", "country", "province_or_state")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("full_name",)}
    inlines = [PhotoInline, SourceInline, VictimTagInline]

    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "full_name",
                    "native_name",
                    "slug",
                    "gender",
                    "age",
                    "date_of_birth",
                    "date_of_death",
                )
            },
        ),
        (
            "Location",
            {"fields": ("city_of_death", "province_or_state", "country")},
        ),
        (
            "Details",
            {
                "fields": (
                    "short_summary",
                    "biography",
                    "occupation",
                    "education",
                    "marital_status",
                    "children_count",
                    "burial_location",
                    "social_links",
                )
            },
        ),
        (
            "Verification",
            {
                "fields": (
                    "verification_status",
                    "verification_notes",
                    "confidence_score",
                )
            },
        ),
        (
            "Private",
            {"fields": ("family_contact_private", "submitted_by")},
        ),
        ("Metadata", {"fields": ("created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        changes = {field: form.cleaned_data.get(field) for field in form.changed_data}
        log_action(request.user, "update" if change else "create", obj, changes)

    def delete_model(self, request, obj):
        log_action(request.user, "delete", obj, model_to_dict(obj))
        super().delete_model(request, obj)


@admin.register(Photo)
class PhotoAdmin(NoDeleteForModerator, admin.ModelAdmin):
    list_display = ("victim", "caption", "order_index", "created_at")
    search_fields = ("victim__full_name", "caption")
    list_filter = ("created_at",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        changes = {field: form.cleaned_data.get(field) for field in form.changed_data}
        log_action(request.user, "update" if change else "create", obj, changes)

    def delete_model(self, request, obj):
        log_action(request.user, "delete", obj, model_to_dict(obj))
        super().delete_model(request, obj)


@admin.register(Source)
class SourceAdmin(NoDeleteForModerator, admin.ModelAdmin):
    list_display = ("victim", "publisher_name", "title", "publication_date")
    search_fields = ("victim__full_name", "title", "publisher_name")
    list_filter = ("publisher_name", "publication_date")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        changes = {field: form.cleaned_data.get(field) for field in form.changed_data}
        log_action(request.user, "update" if change else "create", obj, changes)

    def delete_model(self, request, obj):
        log_action(request.user, "delete", obj, model_to_dict(obj))
        super().delete_model(request, obj)


@admin.register(Tag)
class TagAdmin(NoDeleteForModerator, admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        changes = {field: form.cleaned_data.get(field) for field in form.changed_data}
        log_action(request.user, "update" if change else "create", obj, changes)

    def delete_model(self, request, obj):
        log_action(request.user, "delete", obj, model_to_dict(obj))
        super().delete_model(request, obj)


@admin.register(Submission)
class SubmissionAdmin(NoDeleteForModerator, admin.ModelAdmin):
    list_display = ("id", "victim", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("submitter_name", "submitter_email")
    actions = ["mark_approved", "mark_rejected"]

    def mark_approved(self, request, queryset):
        updated = queryset.update(status=Submission.Status.APPROVED)
        for submission in queryset:
            log_action(request.user, "approve", submission, {"status": "approved"})
        self.message_user(request, f"Approved {updated} submissions.")

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status=Submission.Status.REJECTED)
        for submission in queryset:
            log_action(request.user, "reject", submission, {"status": "rejected"})
        self.message_user(request, f"Rejected {updated} submissions.")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "target_model", "target_id")
    list_filter = ("action", "target_model", "timestamp")
    readonly_fields = ("timestamp", "user", "action", "target_model", "target_id", "changes")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(VictimTag)
class VictimTagAdmin(NoDeleteForModerator, admin.ModelAdmin):
    list_display = ("victim", "tag")
    search_fields = ("victim__full_name", "tag__name")
