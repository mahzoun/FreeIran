from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from victims.models import Photo, Source, Submission, Tag, Victim


class Command(BaseCommand):
    help = "Create default groups and permissions."

    def handle(self, *args, **options):
        moderator, _ = Group.objects.get_or_create(name="Moderator")
        models = [Victim, Photo, Source, Tag, Submission]
        permissions = []
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            permissions.extend(
                Permission.objects.filter(
                    content_type=content_type,
                    codename__in=[
                        f"add_{model._meta.model_name}",
                        f"change_{model._meta.model_name}",
                        f"view_{model._meta.model_name}",
                    ],
                )
            )
        moderator.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS("Moderator group configured."))
