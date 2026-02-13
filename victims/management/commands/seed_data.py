from django.core.management.base import BaseCommand

from victims.models import Source, Tag, Victim


class Command(BaseCommand):
    help = "Seed sample memorial data."

    def handle(self, *args, **options):
        tag_names = ["student", "journalist", "worker"]
        tags = {name: Tag.objects.get_or_create(name=name, slug=name)[0] for name in tag_names}

        victims = [
            {
                "full_name": "Parisa Rahimi",
                "native_name": "پریسا رحیمی",
                "city_of_death": "Tehran",
                "province_or_state": "Tehran",
                "country": "Iran",
                "short_summary": "Remembered for peaceful advocacy and community support.",
                "biography": "Parisa was known for her dedication to education and community work.",
                "verification_status": Victim.VerificationStatus.VERIFIED,
                "confidence_score": 85,
            },
            {
                "full_name": "Amir Hosseini",
                "native_name": "امیر حسینی",
                "city_of_death": "Shiraz",
                "province_or_state": "Fars",
                "country": "Iran",
                "short_summary": "Honored for civic courage and kindness.",
                "biography": "Amir worked as a technician and was active in local support networks.",
                "verification_status": Victim.VerificationStatus.PENDING,
                "confidence_score": 60,
            },
        ]

        for data in victims:
            victim, created = Victim.objects.get_or_create(
                full_name=data["full_name"],
                defaults=data,
            )
            victim.tags.add(tags["student"])
            Source.objects.get_or_create(
                victim=victim,
                title="Community report",
                url="https://example.org/report",
                publisher_name="Community Archive",
                credibility_score=3,
                notes="Sample source entry.",
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created {victim.full_name}"))

        self.stdout.write(self.style.SUCCESS("Seed data complete."))
