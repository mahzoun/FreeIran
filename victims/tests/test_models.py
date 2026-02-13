import datetime

from django.test import TestCase

from victims.models import Victim


class VictimModelTests(TestCase):
    def test_slug_is_generated(self):
        victim = Victim.objects.create(
            full_name="Leila Moradi",
            city_of_death="Tehran",
            province_or_state="Tehran",
            country="Iran",
            date_of_death=datetime.date(2022, 10, 1),
        )
        self.assertTrue(victim.slug)
        self.assertIn("leila", victim.slug)
