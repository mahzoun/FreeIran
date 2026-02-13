from __future__ import annotations

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

import bleach
from PIL import Image


def sanitize_text(value: str) -> str:
    return bleach.clean(value or "", tags=[], strip=True).strip()


def validate_image_size(image) -> None:
    max_bytes = 5 * 1024 * 1024
    if image.size > max_bytes:
        raise ValidationError("Image file size must be under 5MB.")


class Victim(models.Model):
    class VerificationStatus(models.TextChoices):
        UNVERIFIED = "unverified", "Unverified"
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"

    full_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    native_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    city_of_death = models.CharField(max_length=120)
    province_or_state = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    biography = models.TextField(blank=True)
    short_summary = models.TextField(blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    education = models.CharField(max_length=200, blank=True)
    marital_status = models.CharField(max_length=100, blank=True)
    children_count = models.PositiveSmallIntegerField(null=True, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
    )
    verification_notes = models.TextField(blank=True)
    family_contact_private = models.TextField(blank=True)
    burial_location = models.CharField(max_length=200, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    confidence_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)], default=50
    )
    search_vector = SearchVectorField(null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField("Tag", through="VictimTag", related_name="victims")

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["full_name"]),
            models.Index(fields=["city_of_death"]),
            models.Index(fields=["date_of_death"]),
            models.Index(fields=["verification_status"]),
            GinIndex(fields=["search_vector"], name="victim_search_vector_gin"),
        ]

    def __str__(self) -> str:
        return self.full_name

    def clean(self) -> None:
        self.full_name = sanitize_text(self.full_name)
        self.native_name = sanitize_text(self.native_name)
        self.biography = sanitize_text(self.biography)
        self.short_summary = sanitize_text(self.short_summary)
        self.verification_notes = sanitize_text(self.verification_notes)
        self.family_contact_private = sanitize_text(self.family_contact_private)

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base_slug = slugify(self.full_name) or "victim"
            slug = base_slug
            counter = 1
            while Victim.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)
        Victim.objects.filter(pk=self.pk).update(
            search_vector=SearchVector("full_name", "native_name", "biography", "short_summary")
        )


class Photo(models.Model):
    victim = models.ForeignKey(Victim, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to="victims/photos/%Y/%m/",
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png", "webp"]),
            validate_image_size,
        ],
    )
    caption = models.CharField(max_length=255, blank=True)
    photographer_credit = models.CharField(max_length=255, blank=True)
    order_index = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order_index", "created_at"]

    def __str__(self) -> str:
        return f"Photo for {self.victim.full_name}"

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if not hasattr(self.image, "path"):
            return
        try:
            img = Image.open(self.image.path)
        except (FileNotFoundError, ValueError):
            return
        max_width = 2000
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
            img.save(self.image.path, optimize=True, quality=85)


class Source(models.Model):
    victim = models.ForeignKey(Victim, related_name="sources", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=500)
    publisher_name = models.CharField(max_length=255)
    publication_date = models.DateField(null=True, blank=True)
    credibility_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=3
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-publication_date", "title"]

    def __str__(self) -> str:
        return f"{self.publisher_name}: {self.title}"


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class VictimTag(models.Model):
    victim = models.ForeignKey(Victim, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("victim", "tag")

    def __str__(self) -> str:
        return f"{self.victim.full_name} -> {self.tag.name}"


class Submission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    victim = models.ForeignKey(Victim, null=True, blank=True, on_delete=models.SET_NULL)
    submitter_name = models.CharField(max_length=120, blank=True)
    submitter_email = models.EmailField(blank=True)
    proposed_data = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    reviewer_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Submission {self.pk} ({self.get_status_display()})"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("approve", "Approve"),
        ("reject", "Reject"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=120)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.action} {self.target_model} ({self.target_id})"
