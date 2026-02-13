from django.urls import reverse
from rest_framework.test import APITestCase

from victims.models import Victim


class VictimApiTests(APITestCase):
    def setUp(self):
        Victim.objects.create(
            full_name="Neda A.",
            city_of_death="Tehran",
            province_or_state="Tehran",
            country="Iran",
        )

    def test_victim_list(self):
        url = reverse("victim-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["results"])  # pagination
